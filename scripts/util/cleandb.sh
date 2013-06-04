
psql wepp << EOF
  delete from job_queue WHERE request_id IS NOT NULL;
  vacuum full analyze job_queue;
  vacuum;
  \q
EOF
