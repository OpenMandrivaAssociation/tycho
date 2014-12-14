#!/bin/sh
set -e

_prefer_jre="true"
. /usr/share/java-utils/java-functions

set_jvm

set_classpath \
    aether/aether-api \
    atinject \
    beust-jcommander \
    cglib \
    eclipse/osgi \
    google-guice \
    guava \
    objectweb-asm/asm \
    org.eclipse.sisu.inject \
    plexus/utils \
    slf4j/api \
    slf4j/simple \
    tycho/org.fedoraproject.p2 \
    tycho/xmvn-p2-installer-plugin \
    xmvn/xmvn-api \
    xmvn/xmvn-core \

MAIN_CLASS=org.fedoraproject.p2.app.P2InstallerApp
run "$@"
