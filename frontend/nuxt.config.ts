// https://nuxt.com/docs/api/configuration/nuxt-
export default defineNuxtConfig({
  devtools: { enabled: true },
  ssr: false,

  modules: [
    "vuetify-nuxt-module",
    "@vueuse/nuxt",
    "@pinia/nuxt",
    "@nuxt/eslint",
    "nuxt-graphql-client",
    "@hebilicious/vue-query-nuxt",
    "dayjs-nuxt",
    "vue-sonner/nuxt",
    "nuxt-maplibre"
  ],

  app: {
    baseURL: "/ecomon_next/"
  },
  imports: {
    dirs: ["composables/**"]
  },

  srcDir: "./src/",

  runtimeConfig: {
    LOG_FORMAT: "simple",
    public: {
      LOG_LEVEL: "debug",
      GQL_HOST: "http://localhost:8080/v1/graphql",
      API_BASE_URL: "/ecomon",
      "graphql-client": {
        clients: {
          default: {
            schema: "../schema.graphql",
            host: "http://localhost:8080/v1/graphql"
          }
        }
      }
    }
  },

  vuetify: {
    /* vuetify options */
    vuetifyOptions: {
      labComponents: true,

      theme: {
        defaultTheme: "mfnLight",
        themes: {
          mfnLight: {
            dark: false,
            colors: {
              background: "#f0f0f0",
              surface: "#FFFFFF",
              primary: "#043b29", //  '#91bd0d',
              "primary-darken-1": "#003600", // '#7da30b',
              secondary: "#79d827", //  '#174364',
              "secondary-darken-1": "#836500", // '#008786',
              error: "#B00020",
              info: "#2196F3",
              success: "#4CAF50",
              warning: "#FB8C00"
            }
          }
        }
      }
    }
  },

  dayjs: {
    locales: ["en"],
    plugins: ["relativeTime", "timezone"],
    defaultLocale: "de"
  },

  "graphql-client": {
    codegen: {
      silent: true,
      skipTypename: true,
      useTypeImports: true,
      dedupeFragments: true,
      onlyOperationTypes: true,
      avoidOptionals: false,
      disableOnBuild: false,
      maybeValue: "T | null"
    },
    watch: true,
    autoImport: true
  },

  compatibilityDate: "2025-03-12"
});
