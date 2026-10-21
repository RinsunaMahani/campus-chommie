/**
 * Builds the Android app for phone processors only (64-bit and 32-bit ARM), not x86 and x86_64, which only PC
 * emulators and a few Chromebooks use. Those two made 58 MB of the first 140 MB APK, a lot on prepaid data.
 * 32-bit ARM stays for older budget phones.
 */
const { withGradleProperties } = require('expo/config-plugins');

const KEY = 'reactNativeArchitectures';
const PHONES = 'armeabi-v7a,arm64-v8a';

module.exports = function withPhoneArchitectures(config) {
  return withGradleProperties(config, (cfg) => {
    cfg.modResults = cfg.modResults.filter((item) => !(item.type === 'property' && item.key === KEY));
    cfg.modResults.push({ type: 'property', key: KEY, value: PHONES });
    return cfg;
  });
};
