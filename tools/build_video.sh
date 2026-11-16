#!/usr/bin/env bash
# LinkedIn cut: open card, animated part of the film (SH01-SH14, 86 s), info cards, photos, credits.
set -e
cd "$(dirname "$0")/../video"; C=cards; A=../../movie_test/audio; F=../../movie_test/out/lost_and_found_16x9.mp4
seg(){ ffmpeg -v error -y -loop 1 -i "$1" -f lavfi -i anullsrc=r=48000:cl=stereo -vf "fps=24,format=yuv420p,setsar=1,fade=t=in:d=0.7,fade=t=out:st=$(($2-1)):d=1" -map 0:v -map 1:a -t $2 -c:v libx264 -crf 20 -c:a aac -ar 48000 -ac 2 "$3"; }
seg $C/01_open.png 5 s1.mp4; seg $C/02_credits_ran_out.png 6 s3.mp4; seg $C/03_process.png 8 s4.mp4; seg $C/04_screening.png 7 s5.mp4; seg $C/05_credits.png 11 s6.mp4
ffmpeg -v error -y -t 86 -i $F -vf "fade=t=out:st=85:d=1" -af "afade=t=out:st=84.5:d=1.5" -c:v libx264 -crf 20 -c:a aac -ar 48000 -ac 2 s2.mp4
TAIL=32
ffmpeg -v error -y -i s1.mp4 -i s2.mp4 -i s3.mp4 -i s4.mp4 -i s5.mp4 -i s6.mp4 -i $A/ambience.wav -i $A/theme_end.wav -filter_complex "\
[0:v][1:v][2:v][3:v][4:v][5:v]concat=n=6:v=1:a=0[v];\
[6:a]atrim=0:5,afade=t=in:d=1,afade=t=out:st=4:d=1,volume=0.5,aresample=48000,aformat=channel_layouts=stereo[a0];\
[1:a]aresample=48000,aformat=channel_layouts=stereo[a1];\
[7:a]atrim=0:$TAIL,afade=t=in:d=1.5,afade=t=out:st=$((TAIL-4)):d=4,volume=0.6,aresample=48000,aformat=channel_layouts=stereo[a2];\
[a0][a1][a2]concat=n=3:v=0:a=1,alimiter=limit=0.9[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 21 -preset medium -c:a aac -b:a 192k -movflags +faststart lost_and_found_linkedin.mp4
rm -f s?.mp4
