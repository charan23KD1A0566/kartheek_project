#!/bin/bash
# deploy.sh - SIF Sentinel Production Deployment Script
# Usage: ./deploy.sh [environment] [action]
# Example: ./deploy.sh production deploy

set -e

ENVIRONMENT=${1:-production}
ACTION=${2:-deploy}
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; exit 1; }

# Load environment
load_env() {
    if [ "$ENVIRONMENT" = "local" ]; then
        ENV_FILE="$PROJECT_DIR/.env.local"
    else
        ENV_FILE="$PROJECT_DIR/.env.${ENVIRONMENT}"
    fi

    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file not found: $ENV_FILE"
    fi

    log_info "Loading environment from: $ENV_FILE"
    set -a
    source "$ENV_FILE"
    set +a
}

# Validate environment
validate_env() {
    log_info "Validating environment..."

    if [ -z "$MONGODB_URI" ]; then
        log_error "MONGODB_URI not set in environment"
    fi

    if [ -z "$JWT_SECRET" ]; then
        log_error "JWT_SECRET not set in environment"
    fi

    log_success "Environment validation passed"
}

# Build images
build_images() {
    log_info "Building Docker images..."

    docker compose build --no-cache

    log_success "Docker images built successfully"
}

# Deploy services
deploy() {
    log_info "Deploying SIF Sentinel ($ENVIRONMENT)..."

    # Load environment
    load_env
    validate_env

    # Build images
    if [ "$ENVIRONMENT" = "local" ]; then
        log_info "Starting with local MongoDB..."
        docker compose --profile local up -d
    else
        log_info "Starting services (using MongoDB Atlas)..."
        docker compose up -d --no-build
    fi

    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 10

    # Check health
    check_health

    log_success "Deployment completed successfully!"
    log_info "Frontend: http://localhost"
    log_info "Backend API: http://localhost:8000"
    log_info "API Docs: http://localhost:8000/docs"
}

# Check service health
check_health() {
    log_info "Checking service health..."

    # Check backend
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        log_success "Backend API is healthy"
    else
        log_warning "Backend API is not responding yet (may still be starting)"
    fi

    # Check frontend
    if curl -f http://localhost/index.html > /dev/null 2>&1; then
        log_success "Frontend is healthy"
    else
        log_warning "Frontend is not responding yet (may still be starting)"
    fi

    # Show container status
    log_info "Container status:"
    docker compose ps
}

# Stop services
stop() {
    log_info "Stopping services..."
    docker compose down
    log_success "Services stopped"
}

# View logs
view_logs() {
    local service=${1:-}
    if [ -z "$service" ]; then
        log_info "Showing all logs (use Ctrl+C to exit)..."
        docker compose logs -f
    else
        log_info "Showing logs for: $service (use Ctrl+C to exit)..."
        docker compose logs -f "$service"
    fi
}

# Restart services
restart() {
    log_info "Restarting services..."
    docker compose restart
    sleep 5
    check_health
    log_success "Services restarted"
}

# Backup database
backup_db() {
    if [ "$ENVIRONMENT" = "local" ]; then
        log_info "Backing up local MongoDB..."
        BACKUP_DIR="$PROJECT_DIR/backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        docker exec sif_sentinel_mongodb mongodump --out "$BACKUP_DIR"
        
        log_success "Database backed up to: $BACKUP_DIR"
    else
        log_info "Using MongoDB Atlas - configure backups in cloud console"
        log_info "https://www.mongodb.com/cloud/atlas"
    fi
}

# Update application
update() {
    log_info "Updating application..."

    # Pull latest code
    log_info "Pulling latest code..."
    git pull origin main || log_warning "Git pull failed - continue manually"

    # Rebuild images
    log_info "Rebuilding Docker images..."
    docker compose build

    # Restart services
    log_info "Restarting services..."
    docker compose up -d

    sleep 10
    check_health

    log_success "Application updated successfully"
}

# Show usage
show_usage() {
    cat << EOF
SIF Sentinel Deployment Script

Usage: ./deploy.sh [environment] [action]

Environments:
  local       - Local development (with local MongoDB)
  staging     - Staging environment
  production  - Production environment

Actions:
  deploy      - Build and deploy services (default)
  build       - Build Docker images
  start       - Start services
  stop        - Stop services
  restart     - Restart services
  logs        - View service logs
  logs <svc>  - View logs for specific service (backend, frontend, mongodb)
  health      - Check service health
  backup      - Backup database
  update      - Pull latest code and restart
  shell       - Open shell in backend container

Examples:
  ./deploy.sh local deploy           # Deploy locally with MongoDB
  ./deploy.sh production deploy      # Deploy to production with Atlas
  ./deploy.sh production logs        # View production logs
  ./deploy.sh local logs backend     # View backend logs locally
  ./deploy.sh production health      # Check production health
  ./deploy.sh local backup           # Backup local database

EOF
}

# Open shell in container
shell() {
    local container=${1:-sif_sentinel_backend}
    log_info "Opening shell in $container..."
    docker exec -it "$container" /bin/bash || docker exec -it "$container" /bin/sh
}

# Main execution
case "$ACTION" in
    build)
        load_env
        build_images
        ;;
    deploy)
        deploy
        ;;
    start)
        load_env
        docker compose up -d
        check_health
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        view_logs "$3"
        ;;
    health)
        check_health
        ;;
    backup)
        backup_db
        ;;
    update)
        update
        ;;
    shell)
        shell "$3"
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        log_error "Unknown action: $ACTION. Use './deploy.sh help' for usage."
        ;;
esac
