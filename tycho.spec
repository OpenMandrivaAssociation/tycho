%{?_javapackages_macros:%_javapackages_macros}
# Bootstrap build
# Tycho depends on itself, and Eclipse to build but in certain cases
# these requirements may not be satisfiable.

# Set 'tycho_bootstrap' if Tycho from buildroot is broken or non-existent
# This basically uses javac + xmvn to build only the Tycho components
# required to perform a full Tycho build
# Most common usage : A library (in Fedora) used by Tycho's runtime broke API
%global tycho_bootstrap 1
# Set 'eclipse_bootstrap' if Eclipse from buildroot cannot help build Tycho
# This basically provides a location for usage of pre-bundled Eclipse
# Possible uses : Need to build Tycho before Eclipse in fresh buildroot
%global eclipse_bootstrap 0
# When building version under development (non-release)
# %%global snap -SNAPSHOT
%global snap %{nil}

%global fp_p2_sha 4b8f1d
%global fp_p2_version 0.0.1
%global fp_p2_snap -SNAPSHOT

%define __requires_exclude osgi*

Name:           tycho
Version:        0.21.0
Release:        14
Summary:        Plugins and extensions for building Eclipse plugins and OSGI bundles with Maven
Group:          System/Libraries

# license file is missing but all files having some licensing information are ASL 2.0
License:        ASL 2.0 and EPL
URL:            http://eclipse.org/tycho
Source0:        http://git.eclipse.org/c/tycho/org.eclipse.tycho.git/snapshot/tycho-0.21.0.tar.bz2

# this is a workaround for maven-plugin-plugin changes that happened after
# version 2.4.3 (impossible to have empty mojo created as aggregate). This
# should be fixed upstream properly
Source1:        EmptyMojo.java
Source2:        %{name}-scripts.sh
Source3:        %{name}-bootstrap.sh
Source4:        %{name}-debundle.sh
# Fedora Eclipse bundles (needed when Eclipse not present) to build Tycho
%if %{eclipse_bootstrap}
Source5:        eclipse-bootstrap.tar.xz
%endif
# Eclipse Plugin Project supporting filesystem as p2 repository
# https://github.com/rgrunber/fedoraproject-p2
# Generated using 'git archive --prefix=fedoraproject-p2/ -o fedoraproject-p2-%%{fp_p2_sha}.tar %%{fp_p2_sha} && xz fedoraproject-p2-%%{fp_p2_sha}.tar'
Source6:        fedoraproject-p2-%{fp_p2_sha}.tar.xz

Patch0:         %{name}-fix-build.patch
# Upstream builds against maven-surefire 2.12.3
Patch1:         %{name}-maven-surefire.patch
Patch2:         %{name}-fix-surefire.patch
Patch3:         %{name}-use-custom-resolver.patch
Patch4:         %{name}-maven-delegation.patch
# Additional changes needed just for bootstrap build
Patch5:         %{name}-fix-bootstrap-build.patch
# Patch director plugin to only assemble products for the current arch
Patch6:         %{name}-running-env-only.patch

BuildArch:      noarch

BuildRequires:  java-devel
BuildRequires:  maven-local
BuildRequires:  maven-clean-plugin
BuildRequires:  maven-compiler-plugin
BuildRequires:  maven-dependency-plugin
BuildRequires:  maven-install-plugin
BuildRequires:  maven-jar-plugin
BuildRequires:  maven-javadoc-plugin
BuildRequires:  maven-release-plugin
BuildRequires:  maven-resources-plugin
BuildRequires:  maven-verifier
BuildRequires:  objectweb-asm
BuildRequires:  plexus-containers-component-metadata
BuildRequires:  apache-commons-exec
BuildRequires:  decentxml
BuildRequires:  easymock
BuildRequires:  ecj
BuildRequires:  maven-plugin-testing-harness
BuildRequires:  xmvn-parent-pom
%if ! %{tycho_bootstrap}
BuildRequires:  %{name}
%endif
%if %{eclipse_bootstrap}
# Dependencies for Eclipse bundles we use
BuildRequires:  icu4j-eclipse
BuildRequires:  geronimo-annotation
BuildRequires:  sac
BuildRequires:  sat4j
%else
BuildRequires:  eclipse-platform
%endif
BuildRequires:  jetty-http
BuildRequires:  jetty-util
BuildRequires:  jetty-security
BuildRequires:  jetty-server
BuildRequires:  jetty-servlet
BuildRequires:  maven-shared-utils
BuildRequires:  mockito
BuildRequires:	zip

Requires:       apache-commons-exec
Requires:       decentxml
Requires:       maven-local
Requires:       maven-clean-plugin
Requires:       maven-dependency-plugin
Requires:       maven-verifier
Requires:       objectweb-asm
Requires:       ecj
%if ! %{eclipse_bootstrap}
Requires:       eclipse-platform
%endif

# Tycho always tries to resolve all build plugins, even if they are
# not needed during Maven lifecycle.  This means that Tycho will try
# to resolve plugins like clean, deploy or site, which aren't normally
# used during package build.  See rhbz#971301
Requires:       maven-clean-plugin
Requires:       maven-compiler-plugin
Requires:       maven-deploy-plugin
Requires:       maven-install-plugin
Requires:       maven-jar-plugin
Requires:       maven-resources-plugin
Requires:       maven-site-plugin
Requires:       maven-surefire-plugin
%if %{tycho_bootstrap}
BuildRequires:       maven-deploy-plugin
BuildRequires:       maven-site-plugin
%endif


%description
Tycho is a set of Maven plugins and extensions for building Eclipse
plugins and OSGI bundles with Maven. Eclipse plugins and OSGI bundles
have their own metadata for expressing dependencies, source folder
locations, etc. that are normally found in a Maven POM. Tycho uses
native metadata for Eclipse plugins and OSGi bundles and uses the POM
to configure and drive the build. Tycho supports bundles, fragments,
features, update site projects and RCP applications. Tycho also knows
how to run JUnit test plugins using OSGi runtime and there is also
support for sharing build results using Maven artifact repositories.

Tycho plugins introduce new packaging types and the corresponding
lifecycle bindings that allow Maven to use OSGi and Eclipse metadata
during a Maven build. OSGi rules are used to resolve project
dependencies and package visibility restrictions are honored by the
OSGi-aware JDT-based compiler plugin. Tycho will use OSGi metadata and
OSGi rules to calculate project dependencies dynamically and injects
them into the Maven project model at build time. Tycho supports all
attributes supported by the Eclipse OSGi resolver (Require-Bundle,
Import-Package, Eclipse-GenericRequire, etc). Tycho will use proper
classpath access rules during compilation. Tycho supports all project
types supported by PDE and will use PDE/JDT project metadata where
possible. One important design goal in Tycho is to make sure there is
no duplication of metadata between POM and OSGi metadata.



%package javadoc
Summary:        Javadocs for %{name}
Group:          Documentation
Requires:       jpackage-utils

%description javadoc
This package contains the API documentation for %{name}.

%prep
%setup -q -n %{name}-0.21.0

# Prepare fedoraproject-p2
tar -xf %{SOURCE6}

%pom_disable_module org.fedoraproject.p2.tests fedoraproject-p2

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch6 -p1

find tycho-core -iname '*html' -delete

sed -i -e 's/org.apache.maven.it.util.DirectoryScanner/org.apache.maven.shared.utils.io.DirectoryScanner/g' tycho-testing-harness/src/main/java/org/eclipse/tycho/test/AbstractTychoIntegrationTest.java

# Move from org.sonatype.aether to org.eclipse.aether
find . -name "*.java" | xargs sed -i 's/org.sonatype.aether/org.eclipse.aether/g'
find . -name "*.java" | xargs sed -i 's/org.eclipse.aether.util.DefaultRepositorySystemSession/org.eclipse.aether.DefaultRepositorySystemSession/g'
sed -i 's/public int getPriority/public float getPriority/g' tycho-core/src/main/java/org/eclipse/tycho/core/p2/P2RepositoryConnectorFactory.java

# place empty mojo in place
mkdir -p tycho-maven-plugin/src/main/java/org/fedoraproject
pushd tycho-maven-plugin/src/main/java/org/fedoraproject
cp %{SOURCE1} .
popd

# These units cannot be found during a regular build
sed -i '/^<unit id=.*$/d' tycho-bundles/tycho-bundles-target/tycho-bundles-target.target

# We do not ship org.eclipse.jdt.compiler.apt
%pom_remove_dep "org.eclipse.tycho:org.eclipse.jdt.compiler.apt"
%pom_remove_dep "org.eclipse.tycho:org.eclipse.jdt.compiler.apt" tycho-compiler-jdt

# org.ow2.asm:asm-debug-all -> org.ow2.asm:asm-all
%pom_xpath_set "pom:dependency[pom:artifactId='asm-debug-all']/pom:artifactId" "asm-all" tycho-artifactcomparator

# org.hamcrest -> org.hamcrest.core
%pom_xpath_set "pom:requirement[pom:id='org.hamcrest']/pom:id" "org.hamcrest.core" tycho-bundles/org.eclipse.tycho.p2.maven.repository.tests

# we don't have org.apache.commons:commons-compress:jar:sources
%pom_xpath_remove "pom:dependency[pom:classifier='sources' and pom:artifactId='commons-compress']" tycho-p2/tycho-p2-director-plugin


# Bootstrap Build
%if %{eclipse_bootstrap}
tar -xf %{SOURCE5}
%endif

%if %{tycho_bootstrap}

%patch5 -p1

# Perform the 'minimal' (bootstrap) build of Tycho
cp %{SOURCE2} %{SOURCE3} .
bash %{name}-bootstrap.sh %{eclipse_bootstrap}

%patch5 -p1 -R

# Non-Bootstrap Build
%else

# Set some temporary build version so that the bootstrapped build has
# a different version from the nonbootstrapped. Otherwise there will
# be cyclic dependencies.

medadataFile=%{_datadir}/maven-metadata/tycho.xml
sysVer=`grep -C 1 "<artifactId>tycho</artifactId>" %{_mavenpomdir}/JPP.tycho-main.pom | grep "version" | sed 's/.*>\(.*\)<.*/\1/'`
mkdir boot

# Copy Tycho POMs from system repo and set their versions to %%{version}-SNAPSHOT.
for pom in $(grep 'pom</ns1:path>' $medadataFile | sed 's|.*>\(.*\)<.*|\1|'); do
    sed '
    s/$sysVer/%{version}-SNAPSHOT/g
    s/%{fp_p2_version}%{fp_p2_snap}/%{fp_p2_version}/
' <$pom >boot/$(basename $pom)
done

# Update Maven lifecycle mappings for Tycho packaging types provided by tycho-maven-plugin.
cp %{_javadir}/tycho/tycho-maven-plugin.jar boot/tycho-maven-plugin.jar
jar xf boot/tycho-maven-plugin.jar META-INF/plexus/components.xml
sed -i s/$sysVer/%{version}-SNAPSHOT/ META-INF/plexus/components.xml
jar uf boot/tycho-maven-plugin.jar META-INF/plexus/components.xml

# Create XMvn metadata for the new JARs and POMs by customizing system Tycho metadata.
sed '
  s|>/[^<]*/\([^/]*\.pom\)</ns1:path>|>'$PWD'/boot/\1</ns1:path>|
  s|>'$sysVer'</ns1:version>|>%{version}-SNAPSHOT</ns1:version><ns1:compatVersions><ns1:version>%{version}-SNAPSHOT</ns1:version></ns1:compatVersions>|
  s|>'%{fp_p2_version}%{fp_p2_snap}'</ns1:version>|>%{fp_p2_version}</ns1:version><ns1:compatVersions><ns1:version>%{fp_p2_version}</ns1:version></ns1:compatVersions>|
  s|%{_javadir}/tycho/tycho-maven-plugin.jar|'$PWD'/boot/tycho-maven-plugin.jar|
' $medadataFile >boot/tycho-metadata.xml
%mvn_config resolverSettings/metadataRepositories/repository $PWD/boot/tycho-metadata.xml

%endif

# Tests are skipped anyways, so remove some test dependencies
%pom_xpath_remove "pom:dependency[pom:classifier='tests']" tycho-compiler-plugin
%pom_xpath_remove "pom:dependency[pom:classifier='tests']" tycho-packaging-plugin

%build
xmvn -o -Dtycho-version=%{version}-SNAPSHOT -Dmaven.test.skip=true \
-Dmaven.repo.local=$(pwd)/.m2 -Dfedora.p2.repos=$(pwd)/bootstrap \
-f fedoraproject-p2/pom.xml \
clean install org.apache.maven.plugins:maven-javadoc-plugin:aggregate

xmvn -o -DtychoBootstrapVersion=%{version}-SNAPSHOT -Dmaven.test.skip=true \
-Dmaven.repo.local=$(pwd)/.m2 -Dfedora.p2.repos=$(pwd)/bootstrap \
clean install org.apache.maven.plugins:maven-javadoc-plugin:aggregate

%install

cp %{SOURCE2} %{SOURCE4} .

mkdir -p $RPM_BUILD_ROOT%{_javadir}/%{name}
install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}

# fedoraproject-p2 parent
mod=fedoraproject-p2
install -pm 644 $mod/pom.xml $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-$mod.pom
%add_maven_depmap JPP.%{name}-$mod.pom

# fedoraproject-p2
for mod in fedoraproject-p2/{org.fedoraproject.p2,xmvn-p2-installer-plugin}; do
   echo $mod
   aid=`basename $mod`
   install -pm 644 $mod/pom.xml  $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-$aid.pom
   install -m 644 $mod/target/$aid-%{fp_p2_version}%{fp_p2_snap}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}/$aid.jar
   %add_maven_depmap JPP.%{name}-$aid.pom %{name}/$aid.jar -a "org.eclipse.tycho:$aid"
done

# pom and jar installation
for mod in target-platform-configuration tycho-compiler-{jdt,plugin} \
           tycho-{artifactcomparator,core,embedder-api,metadata-model,testing-harness} \
           sisu-equinox/sisu-equinox{-api,-launching,-embedder} \
           tycho-p2/tycho-p2-{facade,plugin,{director,publisher,repository}-plugin} \
           tycho-{maven,packaging,pomgenerator,release/tycho-versions,source}-plugin \
           tycho-bundles/org*  \
           tycho-surefire/{tycho-surefire-plugin,org.eclipse.tycho.surefire.{osgibooter,junit,junit4{,7}}}; do
   echo $mod
   aid=`basename $mod`
   install -pm 644 $mod/pom.xml  $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-$aid.pom
   install -m 644 $mod/target/$aid-%{version}%{snap}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}/$aid.jar
   %add_maven_depmap JPP.%{name}-$aid.pom %{name}/$aid.jar -a "org.eclipse.tycho:$aid"
done

# pom installation
for pommod in tycho-p2 tycho-bundles tycho-surefire \
              tycho-release sisu-equinox; do
   aid=`basename $pommod`
   install -pm 644 $pommod/pom.xml \
               $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-$aid.pom
   %add_maven_depmap JPP.%{name}-$aid.pom -a "org.eclipse.tycho:$aid"
done

# p2 runtime
dir=.m2/org/eclipse/tycho/tycho-bundles-external/%{version}%{snap}
%if ! %{eclipse_bootstrap}
./%{name}-debundle.sh tycho-bundles/tycho-bundles-external/ $dir/tycho-bundles-external-%{version}*.zip $RPM_BUILD_ROOT%{_javadir}/%{name}/tycho-bundles-external-manifest.txt
%endif
install -pm 644 $dir/tycho-bundles-external-%{version}*.pom $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-tycho-bundles-external.pom
install -m 644 $dir/tycho-bundles-external-%{version}*.zip $RPM_BUILD_ROOT%{_javadir}/%{name}/tycho-bundles-external.zip
%add_maven_depmap JPP.%{name}-tycho-bundles-external.pom %{name}/tycho-bundles-external.zip -a "org.eclipse.tycho:tycho-bundles-external"
%if ! %{eclipse_bootstrap}
cp $RPM_BUILD_ROOT%{_javadir}/%{name}/tycho-bundles-external-manifest.txt{,~}  # workaround for rhbz#1139180
%add_maven_depmap org.eclipse.tycho:tycho-bundles-external:txt:manifest:%{version}%{snap} %{name}/tycho-bundles-external-manifest.txt
mv $RPM_BUILD_ROOT%{_javadir}/%{name}/tycho-bundles-external-manifest.txt{~,}  # workaround for rhbz#1139180
%endif

# main
install -pm 644 pom.xml  $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-main.pom
%add_maven_depmap JPP.%{name}-main.pom

# standalone p2 director
%if ! %{eclipse_bootstrap}
./%{name}-debundle.sh tycho-bundles/tycho-standalone-p2-director/ .m2/org/eclipse/tycho/tycho-standalone-p2-director/%{version}%{snap}/tycho-standalone-p2-director-%{version}*.zip
%endif
pushd .m2/org/eclipse/tycho/tycho-standalone-p2-director/%{version}%{snap}/
install -m 644 tycho-standalone-p2-director-%{version}*.zip $RPM_BUILD_ROOT%{_javadir}/%{name}/tycho-standalone-p2-director.zip
install -pm 644 tycho-standalone-p2-director-%{version}*.pom $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-tycho-standalone-p2-director.pom
popd
%add_maven_depmap JPP.%{name}-tycho-standalone-p2-director.pom tycho/tycho-standalone-p2-director.zip -a "org.eclipse.tycho:tycho-standalone-p2-director"

# javadoc
install -dm 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr target/site/api*/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

%if %{eclipse_bootstrap}
# org.eclipse.osgi
osgiJarPath=`find ".m2/org" -name "org.eclipse.osgi_*.jar"`

# http://git.eclipse.org/c/linuxtools/org.eclipse.linuxtools.eclipse-build.git/tree/externalpoms/org.eclipse.osgi.pom
echo '<?xml version="1.0" encoding="UTF-8"?>
<project xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd" xsi:noNamespaceSchemaLocation="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.eclipse.osgi</groupId>
  <artifactId>org.eclipse.osgi</artifactId>
  <version>3.10.0.v20140328-1811</version>
</project>' > JPP.tycho-osgi.pom

install -pm 644 JPP.tycho-osgi.pom $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.tycho-osgi.pom
install -m 644 $osgiJarPath $RPM_BUILD_ROOT%{_javadir}/%{name}/osgi.jar
%add_maven_depmap JPP.%{name}-osgi.pom %{name}/osgi.jar -a "org.eclipse.tycho:org.eclipse.osgi"

# org.eclipse.osgi.compatibility.state
osgiStateJarPath=`find ".m2/org" -name "org.eclipse.osgi.compatibility.state_*.jar"`

# http://git.eclipse.org/c/linuxtools/org.eclipse.linuxtools.eclipse-build.git/tree/externalpoms/org.eclipse.osgi.compatibility.state.pom
echo '<?xml version="1.0" encoding="UTF-8"?>
<project xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd" xsi:noNamespaceSchemaLocation="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.eclipse.osgi</groupId>
  <artifactId>org.eclipse.osgi.compatibility.state</artifactId>
  <version>1.0.0.v20140328-1811</version>
</project>' > JPP.tycho-osgi.compatibility.state.pom

install -pm 644 JPP.tycho-osgi.compatibility.state.pom $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.tycho-osgi.compatibility.state.pom
install -m 644 $osgiStateJarPath $RPM_BUILD_ROOT%{_javadir}/%{name}/osgi.compatibility.state.jar
%add_maven_depmap JPP.%{name}-osgi.compatibility.state.pom %{name}/osgi.compatibility.state.jar -a "org.eclipse.tycho:org.eclipse.osgi.compatibility.state"
%endif

# Symlink XMvn P2 plugin with all dependencies so that it can be loaded by XMvn
install -d -m 755 %{buildroot}%{_datadir}/xmvn/lib/installer/
ln -s %{_javadir}/eclipse/osgi.jar %{buildroot}%{_datadir}/xmvn/lib/installer/
ln -s %{_javadir}/%{name}/xmvn-p2-installer-plugin.jar %{buildroot}%{_datadir}/xmvn/lib/installer/
ln -s %{_javadir}/%{name}/org.fedoraproject.p2.jar %{buildroot}%{_datadir}/xmvn/lib/installer/

%files -f .mfiles
%dir %{_javadir}/%{name}
%{_datadir}/xmvn/lib/installer/*
%doc README.md

%files javadoc
%{_javadocdir}/%{name}

%changelog
* Thu Sep 25 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.21.0-14
- fedoraproject-p2: Fix requires generation bug

* Wed Sep 24 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.21.0-13
- fedoraproject-p2: Allow installation of source bundles

* Mon Sep 22 2014 Roland Grunberg <rgrunber@redhat.com> - 0.21.0-12
- Add Fedora system repos to target definition resolver.
- Look for any IU if IU/Version query fails in target definition resolver.

* Fri Sep 12 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.21.0-11
- fedoraproject-p2: Allow installing the same symlink into separate dropins

* Wed Sep 10 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.21.0-10
- Fix tycho-bundles-external-manifest.txt generation

* Wed Sep 10 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.21.0-9
- fedoraproject-p2: Fix self-dependencies failing builds

* Tue Sep 9 2014 Roland Grunberg <rgrunber@redhat.com> - 0.21.0-8
- Make debundling more resilient to changes.
- fedoraproject-p2: Update to latest (Fix metapackage merging).

* Mon Sep  8 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.21.0-8
- fedoraproject-p2: Import XMvn P2 plugin
- fedoraproject-p2: Fix NPE bug
- fedoraproject-p2: Avoid extracting tycho-bundles-external.zip

* Fri Sep 05 2014 Roland Grunberg <rgrunber@redhat.com> - 0.21.0-7
- Debundle tycho-bundles-external and tycho-standalone-p2-director.
- Resolves: rhbz#789272

* Thu Sep 04 2014 Roland Grunberg <rgrunber@redhat.com> - 0.21.0-6
- Use fedoraproject-p2 to do OSGi bundle discovery.

* Wed Sep 03 2014 Mat Booth <mat.booth@redhat.com> - 0.21.0-5
- Include eclipse features dir in custom resolver

* Wed Sep 03 2014 Roland Grunberg <rgrunber@redhat.com> - 0.21.0-4
- fedoraproject-p2: Do not regenerate IU metadata on every query.

* Thu Aug 28 2014 Mat Booth <mat.booth@redhat.com> - 0.21.0-3
- Perform non-bootstrap build
- Update running-env-only patch

* Wed Aug 27 2014 Roland Grunberg <rgrunber@redhat.com> - 0.21.0-2.1
- fedoraproject-p2: Fix issues with creation of feature IUs.
- fedoraproject-p2: Fix jar corruption bug.

* Thu Aug 21 2014 Roland Grunberg <rgrunber@redhat.com> - 0.21.0-2
- Integrate fedoraproject-p2 into Tycho.

* Thu Jul 24 2014 Roland Grunberg <rgrunber@redhat.com> - 0.21.0-1
- Update to 0.21.0 Release.

* Fri Jul 11 2014 Mat Booth <mat.booth@redhat.com> - 0.20.0-18
- Allow director plugin to only assemble products for the current arch
- Drop some unneeded BR/Rs on surefire (maven-local pulls these in)

* Wed Jul 02 2014 Roland Grunberg <rgrunber@redhat.com> - 0.20.0-17
- Return non-existant expected local path when resolution fails.
- Resolves: rhbz#1114120

* Fri Jun 27 2014 Roland Grunberg <rgrunber@redhat.com> - 0.20.0-16
- Tycho should always delegate artifact resolution to Maven.

* Wed Jun 25 2014 Alexander Kurtakov <akurtako@redhat.com> 0.20.0-15
- Non-bootstrap build now that aarch64 is done.

* Tue Jun 24 2014 Roland Grunberg <rgrunber@redhat.com> - 0.20.0-14.1
- Add swt aarch64 fragment to bootstrap repo.

* Tue Jun 24 2014 Alexander Kurtakov <akurtako@redhat.com> 0.20.0-14
- Full bootstrap build for secondary archs.

* Thu Jun 12 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.20.0-13
- Restore runtime dependencies on XMvn

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.20.0-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Jun  3 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.20.0-11
- Skip intermediary build in non-bootstrap mode
- Resolves: rhbz#1103839
- Remove unneeded XMvn bits

* Fri May 30 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.20.0-10
- Fix runtime dependencies on XMvn in POMs
- Use custom Plexus config to lookup XMvn classes
- Lookup Aether WorkspaceReader using role hint "ide"

* Thu May 29 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.20.0-9
- Don'n install duplicate Maven metadata for sisu-equinox

* Wed May 21 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.20.0-8
- Use .mfiles generated during build

* Fri May 16 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.20.0-7
- Add support for XMvn 2.0

* Tue May 13 2014 Alexander Kurtakov <akurtako@redhat.com> 0.20.0-6
- Make tycho copy licence feature to the system repo.

* Wed Apr 30 2014 Alexander Kurtakov <akurtako@redhat.com> 0.20.0-5
- Non-bootstrap build.

* Tue Apr 29 2014 Alexander Kurtakov <akurtako@redhat.com> 0.20.0-4
- Organize patches.

* Tue Apr 22 2014 Roland Grunberg <rgrunber@redhat.com> - 0.20.0-3
- Add support for compact profiles (Bug 1090003).

* Wed Apr 02 2014 Roland Grunberg <rgrunber@redhat.com> - 0.20.0-2
- Non-bootstrap build.

* Thu Mar 27 2014 Roland Grunberg <rgrunber@redhat.com> - 0.20.0-1.1
- Update to Eclipse Luna (4.4).

* Mon Mar 24 2014 Roland Grunberg <rgrunber@redhat.com> - 0.20.0-1
- Update to 0.20.0 Release.

* Wed Mar 12 2014 Roland Grunberg <rgrunber@redhat.com> - 0.19.0-11
- Respect %%{eclipse_bootstrap} flag in tycho-bootstrap.sh.
- Update Eclipse bootstrap cache.
- Fix Equinox Launcher usage logic in copy-platform-all.

* Thu Mar 06 2014 Roland Grunberg <rgrunber@redhat.com> - 0.19.0-10
- Non-bootstrap build.

* Thu Mar 06 2014 Roland Grunberg <rgrunber@redhat.com> - 0.19.0-9.1
- Do not check %%{_libdir}/eclipse plugins/features folders twice.

* Wed Feb 26 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.19.0-9
- Improve logging and error handling fop copy-platform-all

* Wed Jan 15 2014 Roland Grunberg <rgrunber@redhat.com> - 0.19.0-8
- Perform a pure bootstrap build.
- Fix issues with bootstrap build.

* Thu Jan 09 2014 Roland Grunberg <rgrunber@redhat.com> - 0.19.0-7
- Fix bootstrap build.

* Mon Jan  6 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.19.0-6
- Fix usage of %%add_maven_depmap for zip files
- Resolves: rhbz#1004310

* Mon Dec 9 2013 Alexander Kurtakov <akurtako@redhat.com> 0.19.0-5
- Switch to using %%mvn_build.
- Update BR/R names.
- Adapt to asm5.

* Thu Nov 21 2013 Roland Grunberg <rgrunber@redhat.com> - 0.19.0-4
- Return expected reactor cache location when XMvn resolution fails.

* Wed Nov 20 2013 Roland Grunberg <rgrunber@redhat.com> - 0.19.0-3
- Bump release for rebuild (Bug 1031769).

* Mon Nov 18 2013 Roland Grunberg <rgrunber@redhat.com> - 0.19.0-2
- Reduce length of file lock name when file is in build directory.

* Thu Oct 24 2013 Roland Grunberg <rgrunber@redhat.com> - 0.19.0-1
- Update to 0.19.0 Release.

* Fri Oct 04 2013 Roland Grunberg <rgrunber@redhat.com> - 0.18.1-7
- Do not use XMvn internals (Bug 1015038).

* Thu Oct 3 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.18.1-6
- Adjust to latest Xmvn (workaround for 1015038).

* Mon Sep  9 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.18.1-5
- Add workaround for rhbz#1004310

* Tue Jul 30 2013 Roland Grunberg <rgrunber@redhat.com> - 0.18.1-4
- Improve artifact resolution using XMvn Resolver. (Bug 986900)

* Mon Jul 29 2013 Roland Grunberg <rgrunber@redhat.com> - 0.18.1-3
- Fix Tycho file locking to work in Fedora.
- Skip validateConsistentTychoVersion by default. (Bug 987271)

* Wed Jul 24 2013 Roland Grunberg <rgrunber@redhat.com> - 0.18.1-2
- Non-bootstrap build.

* Wed Jul 24 2013 Roland Grunberg <rgrunber@redhat.com> - 0.18.1-1.1
- Update to use Eclipse Aether.
- Use MavenSession and Plexus to determine state.
- Fix bootstrap build.

* Thu Jul 18 2013 Roland Grunberg <rgrunber@redhat.com> 0.18.1-1
- Make changes to ensure intermediary build succeeds.
- Remove %%Patch6 in favour of call to sed.

* Thu Jul 18 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.18.1-1
- Update to 0.18.1.

* Tue Jul 16 2013 Roland Grunberg <rgrunber@redhat.com> - 0.18.0-5
- Look for maven artifacts using XMvn Resolver.

* Tue Jul 9 2013 Roland Grunberg <rgrunber@redhat.com> 0.18.0-4
- Update to use maven-surefire 2.15 API.

* Fri Jul 5 2013 Alexander Kurtakov <akurtako@redhat.com> 0.18.0-3
- Use _jnidir too when building local p2 repo.

* Thu Jun 6 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.18.0-2
- Add Requires on plugins present in Maven super POM
- Resolves: rhbz#971301

* Tue May 28 2013 Roland Grunberg <rgrunber@redhat.com> 0.18.0-1
- Update to 0.18.0 Release.

* Thu Apr 11 2013 Roland Grunberg <rgrunber@redhat.com> 0.17.0-1
- Fix bootstrap build for potential future use.

* Tue Apr 2 2013 Roland Grunberg <rgrunber@redhat.com> 0.17.0-1
- Update to 0.17.0 Release.

* Mon Mar 18 2013 Roland Grunberg <rgrunber@redhat.com> 0.17.0-0.11.git3351b1
- Non-bootstrap build.

* Mon Mar 18 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.17.0-0.10.git3351b1
- Merge mizdebsk patch with existing custom resolver patch.

* Mon Mar 18 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.17.0-0.9.git3351b1
- Move the patch into better place.

* Mon Mar 18 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.17.0-0.8.git3351b1
- Non-bootstrap build.

* Mon Mar 18 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.17.0-0.7.git3351b1
- Commit the patch.

* Mon Mar 18 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.17.0-0.6.git3351b1
- Use plexus to instantiate workspace reader.

* Sun Mar 17 2013 Roland Grunberg <rgrunber@redhat.com> 0.17.0-0.5.git3351b1
- Non-bootstrap build.

* Fri Mar 15 2013 Roland Grunberg <rgrunber@redhat.com> 0.17.0-0.4.git3351b1
- Update bootstrapped build for 0.17.0-SNAPSHOT to work against 0.16.0.
- Update to Plexus Compiler 2.2 API.

* Thu Feb 28 2013 Roland Grunberg <rgrunber@redhat.com> 0.17.0-0.3.git3351b1
- Update to using Jetty 9 API.

* Mon Feb 25 2013 Roland Grunberg <rgrunber@redhat.com> 0.17.0-0.2.git3351b1
- Set the global default execution environment to JavaSE-1.6.
- Patch clean-up.

* Mon Feb 25 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.17.0-0.1.git3351b1
- Update to latest upstream.
- RHBZ#915194 - API changed in maven-surefire

* Wed Feb 6 2013 Roland Grunberg <rgrunber@redhat.com> 0.16.0-21
- Non-bootstrap build.

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 0.16.0-20.2
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Wed Feb 6 2013 Roland Grunberg <rgrunber@redhat.com> 0.16.0-20.1
- Change BR/R on maven to maven-local for XMvn support.
- Build bootstrapped to fix missing Fedora Maven class.

* Thu Jan 24 2013 Roland Grunberg <rgrunber@redhat.com> 0.16.0-20
- Use TYCHO_MVN_{LOCAL,RPMBUILD} to determine how maven was called.
- Update to maven-surefire 2.13.

* Thu Dec 20 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-19
- Fix upstream Bug 361204.

* Mon Dec 3 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-18
- Add support for more flexible OSGi bundle paths.
- Use OSGi Requires instead of package name.
- Expand Requires to include the Eclipse platform.

* Mon Nov 19 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-17
- Make additional changes to get Tycho building bootstrapped.

* Mon Nov 5 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-16
- Add capability to build without depending on Tycho or Eclipse.

* Sat Oct 20 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-15
- Package org.eclipse.osgi and org.eclipse.jdt.core.

* Fri Oct 19 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-14
- Update to finalized 0.16.0 Release.

* Wed Oct 17 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-13
- Build Tycho properly in one RPM build.
- Update to 0.16.0 Release.

* Thu Oct 11 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-12.d7f885
- Non-bootstrap build.

* Thu Oct 11 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-11.1.d7f885
- Remove dependence on eclipse by use of self-bundled equinox launcher.

* Wed Oct 10 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-11.d7f885
- copy-platform-all should make symlinked jars from %%{_javadir} unique.
- Non-bootstrap build (reset the %%bootstrap flag properly).

* Mon Oct 8 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.16.0-10.d7f885
- Non-bootstrap build.

* Mon Oct 8 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.16.0-9.1.d7f885
- Filter out OSGi dependencies.

* Thu Oct 4 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-9.d7f885
- Non-bootstrap build.

* Thu Oct 4 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-8.1.d7f885
- Fix Bug in overriding of BREE to JavaSE-1.6.

* Wed Oct 3 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-8.d7f885
- Non-bootstrap build.

* Wed Oct 3 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-7.1.d7f885
- Update to latest 0.16.0 SNAPSHOT.
- First attempts to build without cyclic dependency to JDT.

* Mon Aug 27 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-7.df2c35
- Non bootstrap-build.

* Mon Aug 27 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-6.1.df2c35
- Add BR/R on explicit dependency objectweb-asm4.
- Use consistent whitespace in specfile.

* Fri Aug 24 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-6.df2c35
- Non-bootstrap build.

* Thu Aug 23 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-5.1.df2c35
- Set BREE to at least JavaSE-1.6 for all eclipse packaging types.
- Remove unneeded workaround for JSR14 incompatibility of JDK 1.7.

* Wed Aug 15 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-5.df2c35
- Non-bootstrap build.

* Mon Aug 13 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-4.1.df2c35
- Correctly reference objectweb-asm4 and fix local mode resolution bug.
- Update spec file to honour new java packaging guidelines.

* Thu Aug 9 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-4.df2c35
- Non-bootstrap build.

* Thu Aug 9 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-3.1.df2c35
- Add tycho.local.keepTarget flag to bypass ignoring environments.

* Thu Aug 9 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.16.0-3.df2c35
- Non-bootstrap build.

* Thu Aug 9 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.16.0-2.1.df2c35
- Use recommended %%add_maven_depmap. 

* Thu Aug 9 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.16.0-2.df2c35
- Non-bootstrap build.

* Thu Aug 9 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.16.0-1.2.df2c35
- Properly change bootstrap flag.
- Add some git ignores.

* Thu Aug 9 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.16.0-1.1.df2c35
- Install missing tycho-standalone-p2-director.zip.

* Thu Aug 2 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-1.df2c35
- Update to 0.16.0 SNAPSHOT.

* Tue Jul 31 2012 Roland Grunberg <rgrunber@redhat.com> 0.15.0-3
- Non-bootstrap build.

* Tue Jul 31 2012 Roland Grunberg <rgrunber@redhat.com> 0.15.0-2.1
- Ignore defined environments in local mode.

* Mon Jul 30 2012 Roland Grunberg <rgrunber@redhat.com> 0.15.0-2
- Non-bootstrap build.

* Mon Jul 30 2012 Roland Grunberg <rgrunber@redhat.com> 0.15.0-1.1
- Fix copy-platform-all script to properly link %%{_datadir}/eclipse jars.

* Thu Jul 26 2012 Roland Grunberg <rgrunber@redhat.com> 0.15.0-1
- Update to 0.15.0.
- Set BREE to at least JavaSE-1.6 for Eclipse feature bundles.

* Wed Jul 25 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-7
- Non-bootstrap build.

* Mon Jul 23 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-6
- Detect OSGi jars using presence of Bundle-SymbolicName entry (BZ #838513).

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.14.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jun 11 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-5
- Non-bootstrap build.

* Tue May 29 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-4.1
- Fix Tycho Surfire to run Eclipse test bundles.
- Implement automatic creation of a system p2 repository.
- Allow building SWT fragments (BZ #380934).

* Wed May 23 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-4
- Non-bootstrap build.

* Thu May 17 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-3.1
- Set BREE to be at least JavaSE-1.6 for Eclipse OSGi bundles.

* Wed May 16 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-3
- Non-bootstrap build.

* Wed Apr 25 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-2.1
- Implement a custom resolver when running in local mode.
- Use upstream solution for BZ #372395 to fix the build.

* Wed Apr 4 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-2
- Non-bootstrap build.

* Tue Mar 27 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-1.1
- Add missing tycho-testing-harness to be packaged.
- Use %%{_eclipse_base} from eclipse-platform.

* Fri Mar 9 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-1
- Update to 0.14.1 upstream tag.
- Allow building against maven-surefire 2.12 (instead of 2.10).
- Stop symlinking o.e.osgi and o.e.jdt.core into the m2 cache.

* Thu Feb 16 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.0-4
- Non-bootstrap build.

* Tue Feb 14 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.0-3
- Update to 0.14.0 upstream tag.

* Thu Feb 9 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.0-2
- Non-bootstrap build.

* Wed Feb 01 2012 Roland Grunberg <rgrunber@redhat.com> - 0.14.0-1
- Update to 0.14.0.

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.10.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri May 27 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0.12.0-0.1.a74b1717
- Update to new version do bootstrap from scratch

* Fri May 6 2011 Alexander Kurtakov <akurtako@redhat.com> 0.10.0-3
- Non-bootstrap build.

* Tue May  3 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0.10.0-2
- Add README and make build more silent

* Tue Mar 29 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0.10.0-1
- First bootstrapped version
