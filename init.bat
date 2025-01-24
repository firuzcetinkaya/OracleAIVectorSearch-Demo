# PowerShell script to check Docker installation and pull Oracle image

$CR = "container-registry.oracle.com"
$DB_HOST_NAME = "vector-db"
$DB_PORT = 1521
$ORACLE_PASSWD = "Oracle123"
$DB_EXPOSE_PORT = 1529

Write-Host "Checking Docker installation"
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Docker installation found."
} else {
    Write-Host "Docker installation not found. Please install Docker first."
    exit 1
}

Write-Host "Please login to $CR with your Oracle SSO Credentials before proceeding"
docker login $CR

Write-Host "Pulling Oracle 23ai Image from Oracle Container Registry"
$imageName = "container-registry.oracle.com/database/free:latest"
$imageExists = docker images -q $imageName 2>$null

if ($imageExists) {
    Write-Host "$imageName already exists..."
} else {
    docker pull $imageName
}
Write-Host "Running Oracle 23ai Free Docker Image with configured parameters"

# Check if the Docker container exists
$containerExists = docker ps -a -q -f "name=$DB_HOST_NAME"

if ($containerExists) {
    # Check if the container is exited
    $exitedContainer = docker ps -aq -f "status=exited" -f "name=$DB_HOST_NAME"
    if ($exitedContainer) {
        # Cleanup: Start the exited container
        docker start $DB_HOST_NAME
    }
    Write-Host "Docker Image $DB_HOST_NAME is already up and running!"
} else {
    # Run your container
    docker run -td --name $DB_HOST_NAME --hostname $DB_HOST_NAME -p $DB_EXPOSE_PORT:$DB_PORT -e "ORACLE_PWD=$ORACLE_PASSWD" container-registry.oracle.com/database/free:latest
    
    # Wait until the database is ready
    do {
        Start-Sleep -Seconds 1
        $logs = docker logs $DB_HOST_NAME
    } until ($logs -match "DATABASE IS READY TO USE")
    
    Write-Host "DATABASE IS READY TO USE!"
}

# Get Ollama and run (modify according to your OS)
$modelsDir = "models"
New-Item -ItemType Directory -Path $modelsDir -Force

Invoke-WebRequest -Uri "https://ollama.com/download/Ollama-darwin.zip" -OutFile "$modelsDir\Ollama-darwin.zip"
Expand-Archive -Path "$modelsDir\Ollama-darwin.zip" -DestinationPath $modelsDir -Force
Move-Item -Path "$modelsDir/Ollama.app" -Destination "/Applications/Ollama.app"

Start-Process "ollama" "serve" -NoNewWindow
# get llama3.2 and run
Start-Process "ollama" "run llama3.2" -NoNewWindow