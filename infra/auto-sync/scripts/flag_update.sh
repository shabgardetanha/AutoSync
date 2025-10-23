#!/bin/bash
# Usage: ./flag_update.sh <feature_name> <percentage> <environment>
FEATURE=$1
PERCENT=$2
ENV=${3:-production}

echo "Updating $FEATURE rollout to $PERCENT% in $ENV environment..."
# فرض کنید LaunchDarkly CLI یا API را اینجا فراخوانی می‌کنیم
launchdarkly-cli flag:set $FEATURE --env $ENV --percentage $PERCENT
