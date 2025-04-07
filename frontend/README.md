# Ecomon Monitoring Data Analysis Frontend

## Overview

This is a modern web application for monitoring data analysis built with Nuxt 3, a powerful Vue.js framework. The application provides visualization and analysis tools for environmental monitoring data.

## Technology Stack

### Core Framework

- **Nuxt 3**: Full-stack Vue framework with server-side rendering capabilities
- **Vue 3**: Progressive JavaScript framework for building user interfaces
- **TypeScript**: Adds static typing to enhance code quality and developer experience

### State Management & Data Fetching

- **Pinia**: Vue's official state management library
- **Vue Query**: Data fetching and caching library
- **GraphQL**: API query language for efficient data retrieval
- **Tanstack Query**: Data fetching and caching library

### UI Components & Visualization

- **Vuetify 3**: Material Design component framework
- **Plotly.js**: Interactive scientific charting library
- **MapLibre GL**: Open-source maps visualization
- **Vue Audio Visual**: Audio visualization components
- **Vue Sonner**: Toast notification system

### Form Handling & Validation

- **Vee-Validate**: Form validation library
- **Zod**: TypeScript-first schema validation

### Development Tools

- **ESLint & Prettier**: Code quality and formatting tools
- **Husky & lint-staged**: Git hooks for code quality enforcement
- **Nuxt DevTools**: Enhanced development experience

## Structure

The application follows Nuxt's directory structure with:

- `components/`: Reusable Vue components
- `components/base`: Base componentes which wrapped by more specific components
- `components/common`: Components which are used in multiple locations
- `components/data`: Components which query data by them self and are used in multiple other locations
- `components/**`: Componets specific for a page
- `composables/`: Shared composition functions
- `composables/api`: Compositions for api calls
- `pages/`: Application routes
- `plugins/`: Plugins numbered so the are load in the correct order
- `stores/`: Pinia state management
- `public/`: Static assets
- `layouts/`: Page layouts
- `server/`: Server-side logic
- `queries/`: GraphQL queries types and functions are auto generated from this folder
- `utils/`: Utility functions

## Getting Started

```bash
npm install
```

```bash
npm run dev
```
