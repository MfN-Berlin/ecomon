// @ts-check
import prettierConfig from "eslint-config-prettier";
import pluginRecommended from "eslint-plugin-prettier/recommended";

import withNuxt from "./.nuxt/eslint.config.mjs";

export default withNuxt(pluginRecommended, prettierConfig, {
  rules: {
    "vue/no-multiple-template-root": "off",
    "vue/v-slot-style": "off",
    "vue/multi-word-component-names": "off",
    "vue/prop-name-casing": "off",
    'vue/attribute-hyphenation': 'off',
  }
});
