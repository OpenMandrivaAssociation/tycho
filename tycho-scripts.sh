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
osgiLocations=( ${osgiLocations[@]/#/${prefix}} )
osgiLocations+=( ${osgiLocations[@]/${prefix}/} )
osgiLocations=( ${prefix}/extras ${osgiLocations[@]} )
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
        wantedBundles=`removeFromList "${wantedBundles}" "${bsn}"`
      fi
    fi
  done
done

}

function symlinkBundles () {

osgiLocations=( '/usr/share/java' '/usr/lib/java' '/usr/lib*/eclipse' )

wantedBundles=`echo $1 | tr ',' ' '`

for loc in ${osgiLocations[@]} ; do
  for jar in `find ${loc} -name "*.jar"`; do
    bsn=`readBSN ${jar}`
    if [ -n "${bsn}" ]; then
      echo ${wantedBundles} | grep -q "${bsn}"
      if [ $? -eq 0 ]; then
        ln -s ${jar} "${bsn}.jar"
        wantedBundles=`removeFromList "${wantedBundles}" "${bsn}"`
      fi
    fi
  done
done
}

function removeFromList () {
arr=( ${1} )
for (( i=0; i < ${#arr[@]}; i++ )); do
  if [ "${arr[${i}]}" = "$2" ]; then
    arr[${i}]=
  fi
done
echo ${arr[@]}
}

function isolateProject () {
sed -i "/<artifactId>org.eclipse.osgi<\/artifactId>/ a <version>${osgiV}</version>" "$1/pom.xml"
sed -i "/<artifactId>org.eclipse.osgi.compatibility.state<\/artifactId>/ a <version>${osgiV}</version>" "$1/pom.xml"

cp $1/pom.xml $1/pom.xml.bak

sed -i '/<parent>/,/<\/parent>/ d' "$1/pom.xml"
if [ $# -eq 2 ]; then
  sed -i "/<modelVersion>/ a <groupId>org.eclipse.tycho<\/groupId><version>$2<\/version>" "$1/pom.xml"
else
  sed -i "/<modelVersion>/ a <groupId>org.eclipse.tycho<\/groupId><version>${v}<\/version>" "$1/pom.xml"
fi

}

function unifyProject () {

cp $1/pom.xml.bak $1/pom.xml
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
