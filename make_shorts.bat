@echo off
setlocal EnableDelayedExpansion

title YouTube Shorts Batch Converter

echo ============================================
echo     YOUTUBE SHORTS BATCH CONVERTER
echo ============================================
echo.

if not exist "finished_shorts" mkdir "finished_shorts"

REM Detect available hardware encoder
set "ENCODER=libx264"
set "ENCODER_OPTIONS=-preset veryfast -crf 23"

ffmpeg -hide_banner -encoders 2>nul | findstr /C:"h264_nvenc" >nul
if !errorlevel! EQU 0 (
    set "ENCODER=h264_nvenc"
    set "ENCODER_OPTIONS=-preset p4 -cq 23 -b:v 0"
    echo NVIDIA GPU encoder detected.
    goto encoder_ready
)

ffmpeg -hide_banner -encoders 2>nul | findstr /C:"h264_amf" >nul
if !errorlevel! EQU 0 (
    set "ENCODER=h264_amf"
    set "ENCODER_OPTIONS=-quality speed -rc cqp -qp_i 23 -qp_p 23"
    echo AMD GPU encoder detected.
    goto encoder_ready
)

ffmpeg -hide_banner -encoders 2>nul | findstr /C:"h264_qsv" >nul
if !errorlevel! EQU 0 (
    set "ENCODER=h264_qsv"
    set "ENCODER_OPTIONS=-preset faster -global_quality 23"
    echo Intel GPU encoder detected.
    goto encoder_ready
)

echo No supported GPU encoder detected.
echo Using CPU encoding.

:encoder_ready

echo.
echo Encoder selected: !ENCODER!
echo.

set count=0

for %%F in (part_*.mp4) do (

    set /a count+=1

    echo.
    echo ============================================
    echo Processing Part !count!: %%F
    echo ============================================

    ffmpeg -y -hide_banner -stats ^
    -i "%%F" ^
    -filter_complex "[0:v]split=2[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[blur];[fg]scale=1080:-2[main];[blur][main]overlay=(W-w)/2:(H-h)/2,drawtext=text='Part !count!':fontcolor=white:fontsize=72:borderw=5:bordercolor=black:x=(w-text_w)/2:y=120[outv]" ^
    -map "[outv]" ^
    -map 0:a? ^
    -c:v !ENCODER! !ENCODER_OPTIONS! ^
    -pix_fmt yuv420p ^
    -c:a aac -b:a 160k ^
    -movflags +faststart ^
    "finished_shorts\Short_Part_!count!.mp4"

    if !errorlevel! NEQ 0 (
        echo.
        echo ERROR PROCESSING PART !count!
        echo File: %%F
        echo.
        pause
        exit /b 1
    )

)

echo.
echo ============================================
echo ALL DONE!
echo.
echo Processed !count! videos.
echo.
echo Videos are located in:
echo finished_shorts
echo ============================================

pause