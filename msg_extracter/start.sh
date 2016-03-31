#!/bin/bash

PY_VIRTUAL_ENV=$vir/huawei_env
SPARK_CONF=$SPARK_HOME/conf
main_spark_py=./schedule.py
#SPARK_MASTER_IP=Yang.local
#SPARK_MASTER_PORT=7077

# active virtual environment
vir_ps=`echo $PS1 | sed -n 's/^\((.*)\).*/\1/p'`
if [ -z $vir_ps ];then
    source $PY_VIRTUAL_ENV/bin/activate
    echo "active virtual env `basename $PY_VIRTUAL_ENV`"
fi

# init spark master&slave
source $SPARK_CONF/spark-env.sh
spark_master_num=`ps aux| grep spark.deploy.master | wc -l`
if [ ${spark_master_num} -lt 2 ];then
    echo "starting spark-master program ..."
    bash $SPARK_HOME/sbin/start-master.sh
else
    echo "spark masted has already launched"
fi

master_url=`ps aux| grep spark.deploy.master | sed -n 's/.*--ip \([a-zA-Z.]*\) --port \([0-9]*\).*/\1:\2/p'`
master_url=spark://${master_url}
spark_worker_num=`ps aux| grep spark.deploy.worker | wc -l`
if [ ${spark_worker_num} -lt 2 ];then
    echo "starting spark-slaves program ..."
    bash $SPARK_HOME/sbin/start-slave.sh ${master_url} -c $SPARK_WORKER_CORES -m $SPARK_WORKER_MEMORY
else
    echo "spark slaves have already launched"
fi

echo "running ${main_spark_py} now ..."
$SPARK_HOME/bin/spark-submit --master ${master_url} ${main_spark_py} 
