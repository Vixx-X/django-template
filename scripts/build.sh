#!usr/bin/bash

# === Script for building css and javascript === #

ROOT_DIR=$DIR # Get the parent directory

STATIC_DIR_NAME='static'
CSS_NAME_DIR='css'
CSS_OUT_DIR=$ROOT_DIR/$STATIC_DIR_NAME/$CSS_NAME_DIR

JS_NAME_DIR='js'
JS_OUT_DIR=$ROOT_DIR/$STATIC_DIR_NAME/$JS_NAME_DIR

function clean_output_dir(){
  # Remove the contents of a directory

  [ -d $1 ] && rm -r $1 
  [ ! -d $1 ] && mkdir $1
}

function build_css(){
  # Build and minify css files

  clean_output_dir $CSS_OUT_DIR
  npm run build-css  
}

function build_js(){
  # Build and minify javascript files

  clean_output_dir $JS_OUT_DIR
  npm run build-js  
}

function build(){
  build_css
  build_js
}
