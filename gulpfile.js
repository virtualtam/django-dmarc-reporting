const gulp = require('gulp');
const sass = require('gulp-sass');

const STATIC_DIR = 'dmarc_reporting/static/dmarc_reporting'


// Compile SASS
gulp.task('sass', function() {
    return gulp.src([
      'node_modules/bootstrap/scss/bootstrap.scss',
      'frontend/scss/*.scss',
    ]).pipe(sass())
      .pipe(gulp.dest(STATIC_DIR + "/css"));
});

gulp.task('default', ['sass']);
