#! /bin/bash

. $(pwd)/tycho-scripts.sh

eclipse_bootstrap=$1
preV='0.22.0'
v='0.22.0-SNAPSHOT'
osgiV='3.10.0.v20140328-1811'
fp2V='0.0.1-SNAPSHOT'
bundles=()
bundles[0]='tycho-bundles/org.eclipse.tycho.embedder.shared'
bundles[1]='tycho-bundles/org.eclipse.tycho.core.shared'
bundles[2]='tycho-bundles/org.eclipse.tycho.p2.resolver.shared'
bundles[3]='tycho-bundles/org.eclipse.tycho.p2.tools.shared'
bundles[4]='tycho-bundles/org.eclipse.tycho.p2.maven.repository'
bundles[5]='tycho-bundles/org.eclipse.tycho.p2.resolver.impl'
bundles[6]='tycho-bundles/org.eclipse.tycho.p2.tools.impl'

xtraBundles[0]='fedoraproject-p2/org.fedoraproject.p2'

deps[0]=""
deps[1]="tycho-bundles/org.eclipse.tycho.embedder.shared/target/org.eclipse.tycho.embedder.shared-${v}.jar"
deps[2]="tycho-bundles/org.eclipse.tycho.embedder.shared/target/org.eclipse.tycho.embedder.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.core.shared/target/org.eclipse.tycho.core.shared-${v}.jar"
deps[3]="tycho-bundles/org.eclipse.tycho.embedder.shared/target/org.eclipse.tycho.embedder.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.core.shared/target/org.eclipse.tycho.core.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.resolver.shared/target/org.eclipse.tycho.p2.resolver.shared-${v}.jar"
deps[4]="tycho-bundles/org.eclipse.tycho.embedder.shared/target/org.eclipse.tycho.embedder.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.core.shared/target/org.eclipse.tycho.core.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.resolver.shared/target/org.eclipse.tycho.p2.resolver.shared-${v}.jar"
deps[5]="tycho-bundles/org.eclipse.tycho.embedder.shared/target/org.eclipse.tycho.embedder.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.core.shared/target/org.eclipse.tycho.core.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.resolver.shared/target/org.eclipse.tycho.p2.resolver.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.maven.repository/target/org.eclipse.tycho.p2.maven.repository-${v}.jar:fedoraproject-p2/org.fedoraproject.p2/target/org.fedoraproject.p2-${fp2V}.jar"
deps[6]="tycho-bundles/org.eclipse.tycho.embedder.shared/target/org.eclipse.tycho.embedder.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.core.shared/target/org.eclipse.tycho.core.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.resolver.shared/target/org.eclipse.tycho.p2.resolver.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.tools.shared/target/org.eclipse.tycho.p2.tools.shared-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.maven.repository/target/org.eclipse.tycho.p2.maven.repository-${v}.jar:tycho-bundles/org.eclipse.tycho.p2.resolver.impl/target/org.eclipse.tycho.p2.resolver.impl-${v}.jar"

xtraDeps[0]=""

externalDeps[4]="org.eclipse.equinox.common,org.eclipse.equinox.p2.repository,org.eclipse.equinox.p2.metadata,org.eclipse.equinox.p2.core,org.eclipse.equinox.p2.metadata.repository,org.eclipse.equinox.p2.artifact.repository,org.eclipse.osgi"
externalDeps[5]="org.eclipse.core.runtime,org.eclipse.equinox.security,org.eclipse.equinox.frameworkadmin.equinox,org.eclipse.equinox.frameworkadmin,org.eclipse.equinox.p2.core,org.eclipse.equinox.p2.metadata,org.eclipse.equinox.p2.publisher,org.eclipse.equinox.p2.publisher.eclipse,org.eclipse.equinox.p2.artifact.repository,org.eclipse.equinox.p2.metadata.repository,org.eclipse.equinox.p2.director,org.eclipse.equinox.p2.repository,org.eclipse.equinox.p2.updatesite,org.eclipse.core.net,org.eclipse.equinox.common,org.eclipse.osgi,org.eclipse.equinox.preferences"
externalDeps[6]="org.eclipse.equinox.p2.director.app,org.eclipse.equinox.p2.core,org.eclipse.equinox.p2.publisher,org.eclipse.equinox.p2.updatesite,org.eclipse.core.runtime,org.eclipse.equinox.p2.metadata,org.eclipse.equinox.p2.repository,org.eclipse.equinox.p2.repository.tools,org.eclipse.equinox.p2.metadata.repository,org.eclipse.equinox.p2.artifact.repository,org.eclipse.equinox.p2.publisher.eclipse,org.eclipse.equinox.p2.engine,org.eclipse.equinox.p2.director,org.eclipse.osgi,org.eclipse.equinox.common,org.eclipse.equinox.app,org.eclipse.equinox.registry"

xtraExternalDeps[0]="org.eclipse.osgi,org.eclipse.core.runtime,org.eclipse.equinox.common,org.eclipse.equinox.p2.metadata,org.eclipse.equinox.p2.repository,org.eclipse.equinox.p2.core,org.eclipse.equinox.p2.publisher.eclipse,org.eclipse.equinox.p2.publisher,org.eclipse.equinox.p2.touchpoint.eclipse,org.eclipse.equinox.p2.updatesite,org.eclipse.equinox.p2.repository.tools,org.eclipse.equinox.app,slf4j.api"

reactorprojs=( 'tycho-embedder-api' 'tycho-metadata-model' 'sisu-equinox/sisu-equinox-api' 'sisu-equinox/sisu-equinox-embedder' 'tycho-core' 'tycho-packaging-plugin' 'tycho-p2/tycho-p2-facade' 'tycho-maven-plugin' 'tycho-p2/tycho-p2-repository-plugin' 'tycho-p2/tycho-p2-publisher-plugin' 'target-platform-configuration' 'tycho-artifactcomparator' 'sisu-equinox/sisu-equinox-launching' 'tycho-p2/tycho-p2-plugin' 'tycho-compiler-jdt' 'tycho-compiler-plugin' )

for ((i=0; i < ${#xtraBundles[@]}; i++)) ;do
  echo ''
  echo 'Building ' ${xtraBundles[${i}]} '...'
  echo ''
  isolateProject ${xtraBundles[${i}]} ${fp2V}
  minibuild ${xtraBundles[${i}]} "${xtraDeps[${i}]}" ${xtraExternalDeps[${i}]}
  unifyProject ${xtraBundles[${i}]}
done

# TODO: stop minibuild function from hard-coding org/eclipse/tycho GID path
dir=$(pwd)/.m2/org/fedoraproject/p2/org.fedoraproject.p2/
mkdir -p ${dir}
ln -s $(pwd)/.m2/org/eclipse/tycho/org.fedoraproject.p2/${fp2V} ${dir}

for ((i=0; i < ${#bundles[@]}; i++)) ;do
  echo ''
  echo 'Building ' ${bundles[${i}]} '...'
  echo ''
  isolateProject ${bundles[${i}]}
  minibuild ${bundles[${i}]} "${deps[${i}]}" ${externalDeps[${i}]}
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

# Add org.fedoraproject.p2 to target platform for tycho-bundles-external
extras='bootstrap/extras'
mkdir -p ${extras}
fp2Loc=`find .m2 -name "org.fedoraproject.p2-*.jar"`
cp ${fp2Loc} ${extras}

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
osgi.bundles=org.apache.commons.codec,org.apache.commons.logging,org.apache.httpcomponents.httpclient,org.apache.httpcomponents.httpcore,org.eclipse.core.contenttype,org.eclipse.core.jobs,org.eclipse.core.net,org.eclipse.core.runtime@4\:start,org.eclipse.core.runtime.compatibility.registry,org.eclipse.ecf,org.eclipse.ecf.filetransfer,org.eclipse.ecf.identity,org.eclipse.ecf.provider.filetransfer,org.eclipse.ecf.provider.filetransfer.httpclient4,org.eclipse.ecf.provider.filetransfer.httpclient4.ssl,org.eclipse.ecf.provider.filetransfer.ssl,org.eclipse.ecf.ssl,org.eclipse.equinox.app,org.eclipse.equinox.common@2\:start,org.eclipse.equinox.concurrent,org.eclipse.equinox.ds@2\:start,org.eclipse.equinox.frameworkadmin,org.eclipse.equinox.frameworkadmin.equinox,org.eclipse.equinox.launcher,org.eclipse.equinox.p2.artifact.repository,org.eclipse.equinox.p2.core,org.eclipse.equinox.p2.director,org.eclipse.equinox.p2.director.app,org.eclipse.equinox.p2.engine,org.eclipse.equinox.p2.garbagecollector,org.eclipse.equinox.p2.jarprocessor,org.eclipse.equinox.p2.metadata,org.eclipse.equinox.p2.metadata.repository,org.eclipse.equinox.p2.publisher,org.eclipse.equinox.p2.publisher.eclipse,org.eclipse.equinox.p2.repository,org.eclipse.equinox.p2.repository.tools,org.eclipse.equinox.p2.touchpoint.eclipse,org.eclipse.equinox.p2.touchpoint.natives,org.eclipse.equinox.p2.transport.ecf,org.eclipse.equinox.p2.updatesite,org.eclipse.equinox.preferences,org.eclipse.equinox.registry,org.eclipse.equinox.security,org.eclipse.equinox.simpleconfigurator,org.eclipse.equinox.simpleconfigurator.manipulator,org.eclipse.equinox.util,org.eclipse.osgi.services,org.eclipse.osgi.compatibility.state,org.eclipse.tycho.noopsecurity,org.sat4j.core,org.sat4j.pb,org.fedoraproject.p2
osgi.bundles.defaultStartLevel=4
eclipse.product=org.eclipse.equinox.p2.director.app.product
osgi.splashPath=platform\:/base/plugins/org' > 'eclipse/configuration/config.ini'

zip -r "tycho-bundles-external-${v}.zip" 'eclipse'

popd

loc=".m2/org/eclipse/tycho/tycho-bundles-external/${v}"

mkdir -p ${loc}
cp "${tbeTargetDir}/tycho-bundles-external-${v}.zip" ${loc}
cp 'tycho-bundles/tycho-bundles-external/pom.xml' "${loc}/tycho-bundles-external-${v}.pom"

sed -i "s/<equinox\(.*\)VersionMaven>.*<\/equinox\(.*\)VersionMaven>/<equinox\1VersionMaven>${osgiV}<\/equinox\1VersionMaven>/" pom.xml
# xmvn-p2-installer-plugin needs to find the org.eclipse.osgi bundle
sed -i "s/<groupId>org.eclipse.osgi<\/groupId>/<groupId>org.eclipse.tycho<\/groupId>/
        /<artifactId>org.eclipse.osgi<\/artifactId>/ a <version>${osgiV}<\/version>" fedoraproject-p2/xmvn-p2-installer-plugin/pom.xml
