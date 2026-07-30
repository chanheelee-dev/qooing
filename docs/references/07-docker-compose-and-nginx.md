# Docker Compose and nginx

## Mental model

multi-stage build는 build toolchain과 runtime image를 분리한다. backend image에는 Python
runtime과 locked dependencies, bundle만 남고 frontend runtime image에는 nginx와 static
assets만 남는다. Compose service name `backend`가 내부 DNS 이름이 된다.

**English recap:** Containers package production-shaped runtime artifacts; Compose supplies their
network and startup relationship.

## qooing topology

nginx `:8080`은 SPA asset을 제공하고 `/api`를 `backend:8000`으로 proxy한다. backend
`:8000`도 host에 공개해 `/docs`와 direct API debugging을 허용한다. healthcheck가 성공해야
frontend service가 시작된다.

```bash
scripts/smoke-compose.sh
curl http://localhost:8080/api/health
curl http://localhost:8000/docs
docker compose down
```

## Common mistakes

- frontend build stage에 `.env` secret을 copy하는 문제.
- container 내부에서 `localhost:8000`으로 backend를 찾는 문제.
- image에 root user와 writable application tree를 그대로 두는 문제.

## Try it

`docker compose ps`와 `docker compose logs backend`를 함께 보고 health transition과 nginx
startup 순서를 확인한다.

## Further reading

- [Docker multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/)
- [nginx reverse proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
