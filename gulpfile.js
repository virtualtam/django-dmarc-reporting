const gulp = require('gulp');
const csso = require('gulp-csso');
const rename = require('gulp-rename');
const sass = require('gulp-sass');

const STATIC_DIR = 'dmarc_reporting/static/dmarc_reporting'


// Compile SASS
gulp.task('sass', function() {
    return gulp.src([
      'node_modules/bootstrap/scss/bootstrap.scss',
      'frontend/scss/*.scss',
    ]).pipe(sass())
      .pipe(csso())
      .pipe(rename({ suffix: '.min' }))
      .pipe(gulp.dest(STATIC_DIR + "/css"));
});

gulp.task('default', ['sass']);
