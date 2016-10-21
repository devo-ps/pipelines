var gulp = require('gulp');
var sass = require('gulp-sass');

// Prepares the CSS file
gulp.task('default', function() {
    return gulp.src('scss/*.scss')
        .pipe(sass({ includePaths: require('node-bourbon').includePaths }))
        .pipe(gulp.dest('.'));
});

// Prepares assets & watch for changes
gulp.task('development', ['default'], function(callback) {
    gulp.watch('scss/**/*.scss', ['default']);
});
