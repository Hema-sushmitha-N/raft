FROM golang:1.26-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o node-server ./node-server/

FROM alpine:latest
WORKDIR /app
RUN mkdir -p /wal
COPY --from=builder /app/node-server .
ENTRYPOINT ["./node-server"]