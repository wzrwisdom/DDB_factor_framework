#!/bin/bash
# 获取进程pid
if [ $# -ne 1 ]; then
    echo "Error: 请传入当前结点的端口号."
    exit 1
fi
port="$1"
pid=$(lsof -i :$port | awk '$1 == "COMMAND" {next} $NF ~ "(LISTEN)" {print $2}')
if [ -z "$pid" ]; then
  echo "ERROR: 未找到匹配的进程"
  exit -1
fi
# 确定web目录
binDir=$(dirname $(readlink -e /proc/${pid}/exe))
webDir="$binDir/web"
# 确定home目录
workDir=$(pwdx $pid | awk '{print $2}')
cmdline_contents=$(ps -p $pid -o cmd=)
#检查 cmdline_contents 是否包含 -home 启动项
if [[ $cmdline_contents == *"-home"* ]]; then
  # 提取 -home 的参数
  home_param=$(echo "$cmdline_contents" | awk -F ' -home ' '{print $2}' | awk '{print $1}')
  if [ -n "$home_param" ]; then
    if [[ "$home_param" == /* ]]; then
      homeDir="$home_param"
    else
      homeDir="$workDir/$home_param"
    fi
  fi
else
  # 进程启动命令中不包含 -home 启动项
  homeDir="$workDir"
fi
# 确定modules目录
#检查是否包含启动项 -moduleDir 
if [[ $cmdline_contents == *"-moduleDir"* ]]; then
  # 提取 -moduleDir 参数
  moduleDir_param=$(echo "$cmdline_contents" | awk -F ' -moduleDir ' '{print $2}' | awk '{print $1}')
  if [ -n "$moduleDir_param" ]; then
    if [[ "$moduleDir_param" == /* ]]; then
      moduleDir="$moduleDir_param"
    else 
      moduleDir="$homeDir/$moduleDir_param"
    fi
  fi
else 
  #检查是否包含启动项 -config
  if [[ $cmdline_contents == *"-config"* ]]; then
    # 提取 -config 参数
    config_param=$(echo "$cmdline_contents" | awk -F ' -config ' '{print $2}' | awk '{print $1}')
    if [ -n "$config_param" ]; then
      if [[ "$config_param" == /* ]]; then
        configFile="$config_param"
      else 
        configFile="$workDir/$config_param"
      fi
    fi
  else 
    configFile="$workDir/dolphindb.cfg"
  fi
  #检查配置文件是否包含配置项 moduleDir 
  content=$(grep "moduleDir=" "$configFile" | awk -F= '{print $2}')
    if [ -z "$content" ]; then
      # 在配置文件中未找到包含moduleDir的行
      moduleDir="$homeDir/modules"
    else
      if [[ "$content" == /* ]]; then
        moduleDir="$content"
      else 
        moduleDir="$homeDir/$content"
      fi
    fi
fi
# 确认目录是否存在
function CHECK_DIRECTORY(){
  if [ ! -d "$1" ]; then
    # 目录不存在则创建
    mkdir -p "$1"
    if [ $? -eq 0 ]; then
        echo "$1 创建成功"
    else
        echo "$1 创建失败"
    fi
  fi
}
CHECK_DIRECTORY $webDir
CHECK_DIRECTORY $moduleDir
CHECK_DIRECTORY $homeDir
# 更新 web
cp -r ./web/* "$webDir"
if [ $? -eq 0 ]; then
    echo "web $webDir 更新成功"
else
    echo "web $webDir 更新失败"
fi
# 更新 modules
cp -r ./modules/* "$moduleDir"
if [ $? -eq 0 ]; then
    echo "modules $moduleDir 更新成功"
else
    echo "modules $moduleDir 更新失败"
fi
# 更新 built-in
cp -r ./factorLab "$homeDir"
if [ $? -eq 0 ]; then
    echo "built-in $homeDir 更新成功"
else
    echo "built-in $homeDir 更新失败"
fi





