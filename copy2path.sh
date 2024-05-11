#bin /sh

if [ $# -ne 2 ]
  then
    echo 'param 1: original path(file); \nparams2: target path(file)'
    exit 1
fi

echo 'original path(file): ' $1
echo 'target path(file):' $2

# target_path=/Users/gavin/Desktop/temo/target/
for file in  $1/*
do
  if test -f $file
  then
      echo 开始开被文件 $file ， 开始时间$(date "+%Y-%m-%d %H:%M:%S")
      cp $file $2
  else
      echo 开始开被目录 $file， 开始时间$(date "+%Y-%m-%d %H:%M:%S")
      cp -a $file $2
  fi
done


# target_path=/Users/gavin/Desktop/temo/target/
# for file in ./*
# do
#   if test -f $file
#   then
#       echo 开始开被文件 $file ， 开始时间$(date "+%Y-%m-%d %H:%M:%S")
#       cp $file $target_path
#   else
#       echo 开始开被目录 $file， 开始时间$(date "+%Y-%m-%d %H:%M:%S")
#       cp -a $file $target_path
#   fi
# done
