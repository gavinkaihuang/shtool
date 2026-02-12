

#202502
 运行run_cleaners.py 去删除相关的文件
 代替三个脚本
         "delete_small_videos.py",
        "find_and_delete_files.py",
        "delete_empty_folder.py"



#20251217 
添加delete_small_videos.py
用于删除指定目录下小于指定大小的视频文件


#20250916
添加detect_people.py
用于在树莓派上用脚本检测摄像头前的用户移动

#20250828
修改move_and_filter.sh
修改目标目录和源目录的位置，让目标目录作为第一个参数，源目录作为第二个参数。
要求用户确认目录后进行按键确认执行，减少出错概率。

#202508
添加clean_and_move.sh, 整理指定目录的下一层目录，将非mp4和mkv的文件、文件夹都删除。视频文件也只保留100M以上的。
exe: ./clean_and_move.sh source_path target_path

#202405
 准备备份nas中数据，一些简单脚本，解决大文件拷贝，时间过长IO出错问题

