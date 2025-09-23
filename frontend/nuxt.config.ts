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
    head: {
      link: [{ rel: "icon", type: "image/x-icon", href: "/ecomon_next/favicon.ico" }]
    },
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
      },
      // default value, can be overridden in .env file
      dashboardUrl: process.env.NUXT_PUBLIC_DASHBOARD_URL || 'http://localhost:3838/dashboard/'
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
              primary: "#043b29", //  '#91bd0d',
              "primary-darken-1": "#003600", // '#7da30b',
              secondary: "#79d827", //  '#174364',
              "secondary-darken-1": "#836500" // '#008786',
            }
          },
          mfnDark: {
            dark: true,
            colors: {
              primary: "#0fad7c", // Lighter green for better visibility in dark mode
              "primary-darken-1": "#0a8c64", // Adjusted primary darken
              secondary: "#8aea3e", // Brighter secondary for dark mode
              "secondary-darken-1": "#c9a700" // Brighter gold/yellow for dark mode
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