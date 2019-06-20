const { dest, parallel, src } = require('gulp');
const csso = require('gulp-csso');
const rename = require('gulp-rename');
const sass = require('gulp-sass');

const STATIC_DIR = 'dmarc_reporting/static/dmarc_reporting'


// Compile SASS
function css() {
    return src([
      'node_modules/bootstrap/scss/bootstrap.scss',
      'frontend/scss/*.scss',
    ]).pipe(sass())
      .pipe(csso())
      .pipe(rename({ suffix: '.min' }))
      .pipe(dest(STATIC_DIR + "/css"));
}

exports.css = css;
exports.default = parallel(css);
