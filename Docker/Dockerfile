FROM python:3.7

ARG script_name=vola_script_cloud.py

COPY ./$script_name /batchcompute/workdir/$script_name
WORKDIR /batchcompute/workdir

RUN pip3 install pandas numpy oss2
RUN chmod +x /batchcompute/workdir/$script_name

ENV RUNTIME_SCRIPT_NAME=$script_name
CMD python3 ${RUNTIME_SCRIPT_NAME}
