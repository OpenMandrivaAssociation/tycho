#! /bin/bash

function minibuild () {

basedir=$1

src=`cat "${basedir}/build.properties" | grep 'source..' | cut -d'=' -f2 | tr ' ' '\0'`
output=`cat "${basedir}/build.properties" | grep 'output..' | cut -d'=' -f2 | tr ' ' '\0'`
bName=`cat "${basedir}/META-INF/MANIFEST.MF" | grep 'Bundle-SymbolicName:' | sed 's/Bundle-SymbolicName: \([a-zA-Z0-9_.-]*\)\(;\)\?.*/\1/'`
artifactId=`cat "${basedir}/pom.xml" | sed '/<parent>/,/<\/parent>/ d' | grep "<artifactId>" | sed 's/.*<artifactId>\(.*\)<\/artifactId>.*/\1/'`
version=`cat "${basedir}/pom.xml" | grep "<version>" | sed 's/.*<version>\(.*\)<\/version>.*/\1/'`

# External (System) dependencies
if [ $# -eq 3 ]; then
  mkdir -p "${basedir}/target/externalDeps"
  copyBundles $3 "${basedir}/target/externalDeps"
else
  mkdir -p "${basedir}/target"
fi

mkdir -p "${basedir}/${output}"

# Compile
cp=
if [ $# -gt 1 ]; then
  cp='-classpath '$2':'"${basedir}"'/target/externalDeps/*'
fi

javac -d "${basedir}/${output}" \
  $(for file in `find "${basedir}/${src}" -name "*.java"`; \
    do echo -n "${file} "; \
  done;) \
  ${cp}

# Package
pushd ${basedir}
pushd ${output}
classfiles=`for file in $(find . -name "*.class"); do echo -n ' -C '${output} ${file} ; done;`
popd
jar -cfmv "target/${bName}-${version}.jar" 'META-INF/MANIFEST.MF' 'OSGI-INF' 'plugin.xml' 'about.html' 'plugin.properties' ${classfiles}
popd

# Install
loc=".m2/org/eclipse/tycho/${artifactId}/${version}"
mkdir -p ${loc}
cp "${basedir}/target/${bName}-${version}.jar" ${loc}
cp "${basedir}/pom.xml" "${loc}/${bName}-${version}.pom"

}


function copyBundles () {

osgiLocations=( '/usr/share/java' '/usr/lib/java' '/usr/lib*/eclipse' )

if [ ${eclipse_bootstrap} -eq 1 ]; then
prefix="$(pwd)/bootstrap"
osgiLocations+=( ${osgiLocations[@]/#/${prefix}} )
fi

wantedBundles=`echo $1 | tr ',' ' '`
destDir=$2

for loc in ${osgiLocations[@]} ; do
  for jar in `find ${loc} -name "*.jar"`; do
    bsn=`readBSN ${jar}`
    versionline=`unzip -p ${jar} 'META-INF/MANIFEST.MF' | grep 'Bundle-Version:'`
    if [ -n "${bsn}" ]; then
      vers=`echo "${versionline}" | sed 's/Bundle-Version: \([a-zA-Z0-9_.-]*\).*/\1/'`
      echo ${wantedBundles} | grep -q "${bsn}"
      if [ $? -eq 0 ]; then
        cp ${jar} "${destDir}/${bsn}_${vers}.jar"
        wantedBundles=`echo ${wantedBundles} | sed "s/\(${bsn}\s\|\s${bsn}\s\|\s${bsn}\)/ /"`
      fi
    fi
  done
done

}

function isolateProject () {

sed -i '/<parent>/,/<\/parent>/ d' "$1/pom.xml"
sed -i "/<modelVersion>/ a <groupId>org.eclipse.tycho<\/groupId><version>${v}<\/version>" "$1/pom.xml"

sed -i "/<artifactId>org.eclipse.osgi<\/artifactId>/ a <version>${osgiV}</version>" "$1/pom.xml"
}

function unifyProject () {

aid=$(basename $(dirname $1))
if [ "${aid}" = '.' ]; then
  aid='tycho'
fi
sed -i "/<groupId>org.eclipse.tycho<\/groupId><version>${v}<\/version>/ d" "$1/pom.xml"
sed -i "/<modelVersion>/ a <parent>\n<groupId>org.eclipse.tycho<\/groupId>\n<artifactId>${aid}<\/artifactId>\n<version>${preV}<\/version>\n<\/parent>" "$1/pom.xml"

sed -i "/<version>${osgiV}<\/version>/ d" "$1/pom.xml"

}

function readBSN () {

bsn=
manEntryPat="^[a-zA-Z-]*:"
foundBSNLine=0

while read line; do
if [ ${foundBSNLine} -eq 1 ]; then
  echo ${line} | grep -qE ${manEntryPat}
  if [ $? -eq 0 ]; then
    break
  else
    bsn=${bsn}"`echo ${line} | sed 's/\([a-zA-Z0-9_.-]*\)\(;\)\?.*/\1/'`"
  fi
fi

echo ${line} | grep -q "Bundle-SymbolicName:"
if [ $? -eq 0 ]; then
  bsn=`echo ${line} | grep 'Bundle-SymbolicName:' | sed 's/Bundle-SymbolicName: \([a-zA-Z0-9_.-]*\)\(;\)\?.*/\1/'`
  echo ${line} | grep "Bundle-SymbolicName:" | grep -q ";"
  if [ $? -eq 0 ]; then
    break
  fi
  foundBSNLine=1
fi
done < <(unzip -p $1 'META-INF/MANIFEST.MF')

echo ${bsn}

}


eclipse_bootstrap=$1
preV='0.20.0'
v='0.20.0-SNAPSHOT'
osgiV='3.9.1.v20131014-1715'
bundles=()
bundles[0]='tycho-bundles/org.eclipse.tycho.embedder.shared'
bundles[1]='tycho-bundles/org.eclipse.tycho.core.shared'
bundles[2]='tycho-bundles/org.eclipse.tycho.p2.resolver.shared'
bundles[3]='tycho-bundles/org.eclipse.tycho.p2.tools.shared'
bundles[4]='tycho-bundles/org.eclipse.tycho.p2.maven.repository'
bundles[5]='tycho-bundles/org.eclipse.tycho.p2.resolver.impl'
bundles[6]='tycho-bundles/org.eclipse.tycho.p2.tools.impl'

deps[0]=""
deps[1]="tycho-bundles/org.eclipse.tycho.embedder.shared/target/org.eclipse.tycho.embedder.shared-${v}.jar"
deps[2]="tycho-bundles/org.eclipse.tycho.embedder.shared/target/org.eclipse.tycho.embedder.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.core.shared/target/org.eclipse.tycho.core.shared-${v}.jar"
deps[3]="tycho-bundles/org.eclipse.tycho.embedder.shared/target/org.eclipse.tycho.embedder.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.core.shared/target/org.eclipse.tycho.core.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.resolver.shared/target/org.eclipse.tycho.p2.resolver.shared-${v}.jar"
deps[4]="tycho-bundles/org.eclipse.tycho.embedder.shared/target/org.eclipse.tycho.embedder.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.core.shared/target/org.eclipse.tycho.core.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.resolver.shared/target/org.eclipse.tycho.p2.resolver.shared-${v}.jar"
deps[5]="tycho-bundles/org.eclipse.tycho.embedder.shared/target/org.eclipse.tycho.embedder.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.core.shared/target/org.eclipse.tycho.core.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.resolver.shared/target/org.eclipse.tycho.p2.resolver.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.maven.repository/target/org.eclipse.tycho.p2.maven.repository-${v}.jar"
deps[6]="tycho-bundles/org.eclipse.tycho.embedder.shared/target/org.eclipse.tycho.embedder.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.core.shared/target/org.eclipse.tycho.core.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.resolver.shared/target/org.eclipse.tycho.p2.resolver.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.tools.shared/target/org.eclipse.tycho.p2.tools.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.maven.repository/target/org.eclipse.tycho.p2.maven.repository-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.resolver.impl/target/org.eclipse.tycho.p2.resolver.impl-${v}.jar"

externalDeps[4]="org.eclipse.equinox.common,org.eclipse.equinox.p2.repository,org.eclipse.equinox.p2.metadata,org.eclipse.equinox.p2.core,org.eclipse.equinox.p2.metadata.repository,org.eclipse.equinox.p2.artifact.repository,org.eclipse.osgi"
externalDeps[5]="org.eclipse.core.runtime,org.eclipse.equinox.security,org.eclipse.equinox.frameworkadmin.equinox,org.eclipse.equinox.frameworkadmin,org.eclipse.equinox.p2.core,org.eclipse.equinox.p2.metadata,org.eclipse.equinox.p2.publisher,org.eclipse.equinox.p2.publisher.eclipse,org.eclipse.equinox.p2.artifact.repository,org.eclipse.equinox.p2.metadata.repository,org.eclipse.equinox.p2.director,org.eclipse.equinox.p2.repository,org.eclipse.equinox.p2.updatesite,org.eclipse.core.net,org.eclipse.equinox.common,org.eclipse.osgi,org.eclipse.equinox.preferences"
externalDeps[6]="org.eclipse.equinox.p2.director.app,org.eclipse.equinox.p2.core,org.eclipse.equinox.p2.publisher,org.eclipse.equinox.p2.updatesite,org.eclipse.core.runtime,org.eclipse.equinox.p2.metadata,org.eclipse.equinox.p2.repository,org.eclipse.equinox.p2.repository.tools,org.eclipse.equinox.p2.metadata.repository,org.eclipse.equinox.p2.artifact.repository,org.eclipse.equinox.p2.publisher.eclipse,org.eclipse.equinox.p2.engine,org.eclipse.equinox.p2.director,org.eclipse.osgi,org.eclipse.equinox.common,org.eclipse.equinox.app,org.eclipse.equinox.registry"

reactorprojs=( 'tycho-embedder-api' 'tycho-metadata-model' 'sisu-equinox/sisu-equinox-api' 'sisu-equinox/sisu-equinox-embedder' 'tycho-core' 'tycho-packaging-plugin' 'tycho-p2/tycho-p2-facade' 'tycho-maven-plugin' 'tycho-p2/tycho-p2-repository-plugin' 'tycho-p2/tycho-p2-publisher-plugin' 'target-platform-configuration' 'tycho-artifactcomparator' 'sisu-equinox/sisu-equinox-launching' 'tycho-p2/tycho-p2-plugin' 'tycho-compiler-jdt' 'tycho-compiler-plugin' )


for ((i=0; i < ${#bundles[@]}; i++)) ;do
  echo ''
  echo 'Building ' ${bundles[${i}]} '...'
  echo ''
  isolateProject ${bundles[${i}]}
  minibuild ${bundles[${i}]} ${deps[${i}]} ${externalDeps[${i}]}
  unifyProject ${bundles[${i}]}
done

# Can't have empty mojo project
mkdir -p 'tycho-maven-plugin/src/main/java/org/fedoraproject'
pushd 'tycho-maven-plugin/src/main/java/org/fedoraproject'
echo '
package org.fedoraproject;

import org.apache.maven.plugin.MojoExecutionException;
import org.apache.maven.plugin.MojoFailureException;
import org.apache.maven.plugin.AbstractMojo;

/**
 * Empty goal to fix
 * @goal empty
 * @phase clean
 */
public class EmptyMojo
    extends AbstractMojo
{
    public void execute()
        throws MojoExecutionException, MojoFailureException
    {
    }
}
' > EmptyMojo.java
popd

# Run the build on this maven reactor project
for proj in ${reactorprojs[@]} ; do
  isolateProject ${proj}
  xmvn -o -f "${proj}/pom.xml" -Dmaven.repo.local=$(pwd)/.m2 -Dmaven.test.skip=true clean install
  unifyProject ${proj}
done

# Tycho Bundles External (needed for Tycho's OSGi Runtime)
tbeDir='tycho-bundles/tycho-bundles-external'
tbeTargetDir="${tbeDir}/target"
wantedBundles=`sed 's/ fragment=\"true\"//' "${tbeDir}/tycho-bundles-external.product" | sed -n 's/.*<plugin id=\"\(.*\)\"\/>.*/\1/ p'`

mkdir -p ${tbeTargetDir}'/eclipse/plugins'
copyBundles "${wantedBundles}" "${tbeTargetDir}/eclipse/plugins"

pushd ${tbeTargetDir}

echo "#Eclipse Product File
#Thu Dec 19 21:40:37 EST 2013
version=${v}
name=org.eclipse.tycho.p2
id=tycho-bundles-external" > 'eclipse/.eclipseproduct'

mkdir -p 'eclipse/configuration'

echo '#Product Runtime Configuration File
#Thu Dec 19 21:40:37 EST 2013
osgi.bundles=org.apache.commons.codec,org.apache.commons.logging,org.apache.httpcomponents.httpclient,org.apache.httpcomponents.httpcore,org.eclipse.core.contenttype,org.eclipse.core.jobs,org.eclipse.core.net,org.eclipse.core.runtime@4\:start,org.eclipse.core.runtime.compatibility.registry,org.eclipse.ecf,org.eclipse.ecf.filetransfer,org.eclipse.ecf.identity,org.eclipse.ecf.provider.filetransfer,org.eclipse.ecf.provider.filetransfer.httpclient4,org.eclipse.ecf.provider.filetransfer.httpclient4.ssl,org.eclipse.ecf.provider.filetransfer.ssl,org.eclipse.ecf.ssl,org.eclipse.equinox.app,org.eclipse.equinox.common@2\:start,org.eclipse.equinox.concurrent,org.eclipse.equinox.ds@2\:start,org.eclipse.equinox.frameworkadmin,org.eclipse.equinox.frameworkadmin.equinox,org.eclipse.equinox.launcher,org.eclipse.equinox.p2.artifact.repository,org.eclipse.equinox.p2.core,org.eclipse.equinox.p2.director,org.eclipse.equinox.p2.director.app,org.eclipse.equinox.p2.engine,org.eclipse.equinox.p2.garbagecollector,org.eclipse.equinox.p2.jarprocessor,org.eclipse.equinox.p2.metadata,org.eclipse.equinox.p2.metadata.repository,org.eclipse.equinox.p2.publisher,org.eclipse.equinox.p2.publisher.eclipse,org.eclipse.equinox.p2.repository,org.eclipse.equinox.p2.repository.tools,org.eclipse.equinox.p2.touchpoint.eclipse,org.eclipse.equinox.p2.touchpoint.natives,org.eclipse.equinox.p2.transport.ecf,org.eclipse.equinox.p2.updatesite,org.eclipse.equinox.preferences,org.eclipse.equinox.registry,org.eclipse.equinox.security,org.eclipse.equinox.simpleconfigurator,org.eclipse.equinox.simpleconfigurator.manipulator,org.eclipse.equinox.util,org.eclipse.osgi.services,org.eclipse.tycho.noopsecurity,org.sat4j.core,org.sat4j.pb
osgi.bundles.defaultStartLevel=4
eclipse.product=org.eclipse.equinox.p2.director.app.product
osgi.splashPath=platform\:/base/plugins/org' > 'eclipse/configuration/config.ini'

zip -r "tycho-bundles-external-${v}.zip" 'eclipse'

popd

loc=".m2/org/eclipse/tycho/tycho-bundles-external/${v}"

mkdir -p ${loc}
cp "${tbeTargetDir}/tycho-bundles-external-${v}.zip" ${loc}
cp 'tycho-bundles/tycho-bundles-external/pom.xml' "${loc}/tycho-bundles-external-${v}.pom"

sed -i "s/<equinoxVersion>.*<\/equinoxVersion>/<equinoxVersion>${osgiV}<\/equinoxVersion>/" pom.xml
