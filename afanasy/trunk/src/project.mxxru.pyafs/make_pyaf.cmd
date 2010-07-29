SET MXX_RU_CPP_TOOLSET=vc9

set output=..\..\bin_pyaf\%AF_PYAFVER%
set pyaf=tmp\%AF_PYAFVER%\pyaf.pyd

if exist %QTDIR%\bin\qtvars.bat call %QTDIR%\bin\qtvars.bat

call %MSVCPATH%\vcvarsall.bat %1

ruby afanasy.mxw.rb

if not exist %output% mkdir %output%
copy %pyaf% %output%