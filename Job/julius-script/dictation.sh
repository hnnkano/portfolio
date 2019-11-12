#!/bin/sh
#julius -C julius-script/realtime.jconf -dnnconf julius-4.5/dictation-kit-v4.4/dictation.dnnconf -module  > /dev/null &
julius -C julius-script/dictation.jconf -dnnconf julius-4.5/dictation-kit-4.5/julius.dnnconf -module &
