
sleep 2
sudo uhubctl -a off -p 1 -l 1-1
sleep 5 
sudo uhubctl -a on -p 1 -l 1-1
sleep 5
sudo uhubctl
sleep 2 
sudo chmod 777 /dev/tty*
sleep 2
sudo chmod 777 /dev/vid*
sleep 2
sudo chmod 777 /dev/i2c*
sleep 3
sudo chmod -R 777 /dev/gpiomem*
