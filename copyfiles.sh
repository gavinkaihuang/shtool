#bin /sh

target_path=/Users/gavin/Desktop/temo/target/
for file in ./*
do
  if test -f $file
  then
      echo 开始开被文件 $file ， 开始时间$(date "+%Y-%m-%d %H:%M:%S")
      cp $file $target_path
  else
      echo 开始开被目录 $file， 开始时间$(date "+%Y-%m-%d %H:%M:%S")
      cp -a $file $target_path
  fi
done
