import svelte from 'rollup-plugin-svelte';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from 'rollup-plugin-commonjs';
import postcss from 'rollup-plugin-postcss';
import typescript from '@rollup/plugin-typescript';
import sveltePreprocessor from 'svelte-preprocess';
import html2 from 'rollup-plugin-html2';
import livereload from 'rollup-plugin-livereload';
import serve from 'rollup-plugin-serve';
import { terser } from 'rollup-plugin-terser';

const production = process.env.NODE_ENV !== 'development';

const plugins = [
  svelte({
    emitCss: true,
    // generate: 'ssr',
    // hydratable: true,
    dev: !production,
    preprocess: sveltePreprocessor()
  }),
  typescript(),
  resolve({
    browser: true,
    dedupe: importee => importee === 'svelte' || importee.startsWith('svelte/')
  }),
  commonjs(),
  postcss({
    extract: true,
    minimize: true,
    use: [
      ['sass', {
        includePaths: [
          './theme',
          './node_modules'
        ]
      }]
    ]
  }),
  html2({
    template: 'app.html'
  })
];

if (!production) {
  plugins.push(
    serve({
      contentBase: './dist',
      open: false
    }),
    livereload({ watch: './dist' })
  );
} else {
  plugins.push(terser());
}

module.exports = {
  input: 'index.js',
  output: {
    file: 'dist/bundle.js',
    format: 'iife',
    name: 'app'
  },
  plugins: plugins,
  watch: {
    clearScreen: false
  }
};
