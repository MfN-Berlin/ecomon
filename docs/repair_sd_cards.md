# Restore broken Wildlifeacoustics SD-Cards
Tools and Instructions to restore your broken wildlife acoustics recorder sd cards

This guide will help you recover all files from a damaged or corrupted SD card using `PhotoRec`, tool that comes with the `TestDisk` suite.
With the help of the python script in this repository you will be able to restore filenames from wildlefeacoustics WAV headers.


## Prerequisites

- A computer running Linux (e.g., Ubuntu, Fedora)
- An SD card reader
- `TestDisk/PhotoRec` installed on your system
- local copy of this repository
- installed Pythonpackage `guano`

## Step 1: Install TestDisk/PhotoRec

### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install testdisk
```
### Fedora:
```bash
sudo dnf install testdisk
```
## Step 2: Rescue files from SD-Card
### Step 2.1: Create a folder to store the restored files
```bash
mkdir restore
```
### Step 2.2 Insert SDCard and start photorec
```bash
sudo photorec
```
1. Select SD-Card
```bash
PhotoRec 7.2, Data Recovery Utility, February 2024
Christophe GRENIER <grenier@cgsecurity.org>
https://www.cgsecurity.org

  PhotoRec is free software, and
comes with ABSOLUTELY NO WARRANTY.

Select a media and choose 'Proceed' using arrow keys:
>Disk /dev/sda - 1000 GB / 931 GiB (RO) - Extreme 55AE
 Disk /dev/sdb - 511 GB / 476 GiB (RO) - MassStorageClass
 Disk /dev/mapper/luks-a9bcfb12-f9ef-4c23-9858-fe3f06b3c57b - 1719 GB / 1601 GiB (RO)
 Disk /dev/dm-0 - 1719 GB / 1601 GiB (RO)
 Disk /dev/nvme0n1 - 2000 GB / 1863 GiB (RO) - Samsung SSD 990 PRO 2TB

```
2. Select Partition
```bash
PhotoRec 7.2, Data Recovery Utility, February 2024
Christophe GRENIER <grenier@cgsecurity.org>
https://www.cgsecurity.org

Disk /dev/sdb - 511 GB / 476 GiB (RO) - MassStorageClass

     Partition                  Start        End    Size in sectors
      No partition             0   0  1 62231  39 16  999743488 [Whole disk]
> 1 P HPFS - NTFS              4  20 17 62231  39 16  999677952

```

3. Select possible filesystems:
```bash
PhotoRec 7.2, Data Recovery Utility, February 2024
Christophe GRENIER <grenier@cgsecurity.org>
https://www.cgsecurity.org

 1 P HPFS - NTFS              4  20 17 62231  39 16  999677952

To recover lost files, PhotoRec needs to know the filesystem type where the
file were stored:
 [ ext2/ext3 ] ext2/ext3/ext4 filesystem
>[ Other     ] FAT/NTFS/HFS+/ReiserFS/...

```
4. Select target folder you created in step 2.1 and start with pressing `c`
```bash

PhotoRec 7.2, Data Recovery Utility, February 2024

Please select a destination to save the recovered files to.
Do not choose to write the files to the same partition they were stored on.
Keys: Arrow keys to select another directory
      C when the destination is correct
      Q to quit
Directory /home/§§§
§§§@pc:~$ 000       920  5-Sep-2024 12:19 .
 drwxr-xr-x     0     0         8  1-Sep-2024 14:26 ..
 drwxr-xr-x  1000  1000        20  1-Sep-2024 13:46  ~
 drwxr-xr-x  1000  1000        30  5-Sep-2024 12:17 Bilder
 drwxr-xr-x  1000  1000       110  4-Sep-2024 17:20 Dokumente
 drwxr-xr-x  1000  1000       308  4-Sep-2024 17:50 Downloads
 drwxr-xr-x  1000  1000         0  1-Sep-2024 12:35 Musik
 drwxr-xr-x  1000  1000         0  1-Sep-2024 12:35 Schreibtisch
 drwxr-xr-x  1000  1000         0  1-Sep-2024 12:35 Videos
 drwxr-xr-x  1000  1000         0  1-Sep-2024 12:35 Vorlagen
>drwxr-xr-x  1000  1000         0  5-Sep-2024 12:13 restore
 drwxr-xr-x  1000  1000         0  1-Sep-2024 12:35 Öffentlich
```

This process can take a considerable time. After it is completed, you will get a folder structure similar to this.
```bash
.:
insgesamt 0
drwxr-xr-x. 1 §§§ §§§    20  4. Sep 19:41 recup_dir.1
drwxr-xr-x. 1 §§§ §§§ 12020  4. Sep 22:07 recup_dir.2
drwxr-xr-x. 1 §§§ §§§ 12000  4. Sep 22:07 recup_dir.3
...

./recup_dir.1:
insgesamt 4
-rw-r--r--. 1 §§§ §§§ 1492  4. Sep 20:56 report.xml

./recup_dir.2:
insgesamt 1845012
-rw-r--r--. 1 §§§ §§§  262144  4. Sep 22:06 f0067584.txt
-rw-r--r--. 1 §§§ §§§ 1712710  4. Sep 22:06 f0068096.wav
-rw-r--r--. 1 §§§ §§§ 4610630  4. Sep 22:06 f0071680.wav
...
```

## 5.Rename files based on Metadata
Clone Clone https://github.com/likt0r/restore-wildlifeacoustics-sd-cards to your local machine.

Use the python script rename_broken_files.py

```bash
# --move will move not copy the files to new target folder with new names
# --group-by-month will create subfolders prefix_YYYYMM and copy/move all files ov the month in it
python rename_broken_files.py ~/restore ~/target
```
