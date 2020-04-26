#bin/bash
wordpressDbUserPass="adsfkjs13233409i7adf8"
wordpressDB="wordpressDB"
wordpressUser="wordpressUser"
shortTermBackupsToKeep=3
longTermBackupsToKeep=5
localShortTermLocation="/backups/shortTerm"
s3BucketShortTermLocation="minecraft-server-personal/backups/shortTerm"
localLongTermLocation="/backups/longTerm"
s3BucketLongTermLocation="minecraft-server-personal/backups/longTerm"

mysqldump -u "$wordpressUser" --password="$wordpressDbUserPass"  $wordpressDB > /backups/$wordpressDB-$(date +%d-%m-%Y-%H:%M:%S).zip

###########################

usage() { echo "$0 usage:" && grep " .)\ #" $0; exit 0; }

while getopts ":sblrhaxm"  opt; do
  case $opt in
    s) #Saves the Server
      echo "$(date +%d-%m-%Y-%H:%M:%S) Saving Minecraft Server"
      tmux send-keys -t 'Minecraft' 'save-all' Enter
      ;;

    b) #Backups up the server to the local disk and s3, does not save the server, must specify -s
      echo "$(date +%d-%m-%Y-%H:%M:%S) ######################"
      echo "$(date +%d-%m-%Y-%H:%M:%S) ### Backup started ###"
      echo "$(date +%d-%m-%Y-%H:%M:%S) ######################"

      sleep 10
      echo "$(date +%d-%m-%Y-%H:%M:%S) Backing up Minecraft Server"
      tmux send-keys -t 'Minecraft' 'say Backing up server' Enter

      echo "$(date +%d-%m-%Y-%H:%M:%S) Taking backup"
      zip -r "$localShortTermLocation/backup-$(date +%d-%m-%Y-%H:%M:%S).zip" /Minecraft_Server/

      shortTermBackupNumber=$( ls $localShortTermLocation -l | grep -v total | wc -l )
       if [ $shortTermBackupNumber -gt $shortTermBackupsToKeep ]; then
           echo "$(date +%d-%m-%Y-%H:%M:%S) deleting oldest shortTerm backup"
           sudo rm $(find $localShortTermLocation -type f -printf '%T+ %p\n' | sort | head -n 1 | cut -d " " -f 2)
       fi

       echo "$(date +%d-%m-%Y-%H:%M:%S) Upload backup to S3"
       aws s3 sync $localShortTermLocation/ "s3://$s3BucketShortTermLocation"

      echo "$(date +%d-%m-%Y-%H:%M:%S) ########################"
      echo "$(date +%d-%m-%Y-%H:%M:%S) ### Backup completed ###"
      echo "$(date +%d-%m-%Y-%H:%M:%S) ########################"
      ;;

    l) #LongTerm backup storage locally and to s3
      echo "$(date +%d-%m-%Y-%H:%M:%S) Moving backup to long term storage"
      sleep 20
      #Move oldest file to longterm dir
      mv $localShortTermLocation/$(ls -Art $localShortTermLocation | tail -n 1) $localLongTermLocation/

      longTermBackupNumber=$( ls $localLongTermLocation -l | grep -v total | wc -l )
      if [ $longTermBackupNumber -gt $longTermBackupsToKeep ]; then
         echo "$(date +%d-%m-%Y-%H:%M:%S) deleting oldest longTerm backing"
         sudo rm $(find $localLongTermLocation/ -type f -printf '%T+ %p\n' | sort | head -n 1 | cut -d " " -f 2)
      fi

      echo "$(date +%d-%m-%Y-%H:%M:%S) Upload backup to S3"
      aws s3 sync $localLongTermLocation/ s3://$s3BucketLongTermLocation
      ;;

    r) #restarts the Server
      echo "$(date +%d-%m-%Y-%H:%M:%S) Restarting server"
      tmux send-keys -t 'Minecraft' "say Server is being restarted to free up Memory" Enter
      tmux send-keys -t 'Minecraft' 'save-all' Enter
      tmux send-keys -t 'Minecraft' "say Bye-bye" Enter
      sleep 3
      #watch log file until see "[Server thread/INFO]: Saved the game"
      tmux send-keys -t 'Minecraft' 'stop' Enter
      #watch log file until see "[Server thread/INFO]: ThreadedAnvilChunkStorage (world): All chunks are saved"
      sleep 5
      tmux send-keys -t 'Minecraft' 'sudo java -Xmx4G -Xms1G -jar server.jar nogui' Enter
      ;;

    m) #Echos memory usage to server
      #Creates new tmux session if none exists, otherwise does nothing
      mem=$(echo "$(grep MemFree  /proc/meminfo | grep -o '[0-9]*') / 1024 " | bc)
      echo "Available memory: $mem"
      tmux send-keys -t 'Minecraft' "say Available memory: $mem m" Enter
      ;;

    a) #Starts the Minecraft Server
      #Creates new tmux session if none exists, otherwise does nothing
      tmux new-session -d -s Minecraft
      #CD into Minecraft dir and starts server
      tmux send-keys -t 'Minecraft' 'cd /Minecraft_Server' Enter
      tmux send-keys -t 'Minecraft' 'sudo java -Xmx4G -Xms1G -jar server.jar nogui' Enter
      ;;

    x) #Stops the Minecraft Server
      echo "$(date +%d-%m-%Y-%H:%M:%S) Stopping server"
      tmux send-keys -t 'Minecraft' "say Server is being stopped" Enter
      tmux send-keys -t 'Minecraft' 'save-all' Enter
      tmux send-keys -t 'Minecraft' "say Bye-bye" Enter
      tmux send-keys -t 'Minecraft' "stop" Enter
      ;;

    h | *) # Display help.
      usage
      exit 0
      ;;
  esac
done
