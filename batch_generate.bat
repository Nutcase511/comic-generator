@echo off
chcp 65001 >nul
echo ======================================
echo   批量生成AI漫画
echo ======================================
echo.

cd /d "%~dp0"

:: 主题列表
set "topics=孙悟空在现代办公室^
钢铁侠学做中国菜^
路飞在沙漠中找水^
柯南破解密室之谜"

:: 逐个生成
for %%t in (%topics%) do (
    echo.
    echo [正在生成] %%t
    echo %%t | python main.py
    echo [完成] %%t
    echo.
)

echo ======================================
echo   全部完成！
echo ======================================
pause
