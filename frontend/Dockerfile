FROM oven/bun:1.3.14 AS deps
WORKDIR /app
COPY package.json bun.lock* ./
RUN bun install --frozen-lockfile

FROM deps AS build
COPY . .
RUN bun run build

FROM oven/bun:1.3.14-slim
WORKDIR /app
COPY --from=build /app/build ./build
COPY --from=build /app/package.json .

ENV NODE_ENV=production
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD bun -e "const r = await fetch('http://localhost:3000'); if (!r.ok) process.exit(1)" || exit 1

CMD ["bun", "./build/index.js"]
