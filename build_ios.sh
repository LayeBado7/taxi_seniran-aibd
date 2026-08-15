#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../mobile"
flutter pub get
flutter analyze
flutter build ipa --release
