import subprocess

def run_docker_command(args):
    """Execute Docker CLI commands with error handling."""
    try:
        process = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return process.stdout.strip(), ""
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip()

def get_docker_contexts():
    """Dynamically retrieve Docker contexts."""
    output, err = run_docker_command(["docker", "context", "ls", "--format", "{{.Name}}"])
    if err:
        return [], err
    contexts = output.splitlines()
    return contexts, ""

def get_containers_for_context(context):
    """Get containers for a specific Docker context."""
    output, err = run_docker_command([
        "docker", "--context", context, "ps", "-a", "--format", "{{.Names}}\t{{.Status}}"
    ])
    containers = []
    if err:
        return containers, err
    if output:
        for line in output.splitlines():
            try:
                name, status = line.split("\t")
                containers.append({"name": name, "status": status, "context": context})
            except ValueError:
                continue
    return containers, ""

def get_images_for_context(context):
    """Get images for a specific Docker context."""
    output, err = run_docker_command([
        "docker", "--context", context, "images", "--format", "{{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.Size}}"
    ])
    images = []
    if err:
        return images, err
    if output:
        for line in output.splitlines():
            try:
                name, image_id, size = line.split("\t")
                images.append({
                    "name": name, 
                    "id": image_id, 
                    "size": size, 
                    "context": context
                })
            except ValueError:
                continue
    return images, ""

def get_volumes_for_context(context):
    """Get volumes for a specific Docker context."""
    output, err = run_docker_command([
        "docker", "--context", context, "volume", "ls", "--format", "{{.Name}}\t{{.Driver}}\t{{.Mountpoint}}"
    ])
    volumes = []
    if err:
        return volumes, err
    if output:
        for line in output.splitlines():
            try:
                parts = line.split("\t")
                name = parts[0]
                driver = parts[1] if len(parts) > 1 else "N/A"
                mountpoint = parts[2] if len(parts) > 2 else "N/A"
                
                volumes.append({
                    "name": name, 
                    "driver": driver, 
                    "mountpoint": mountpoint, 
                    "context": context
                })
            except ValueError:
                continue
    return volumes, ""

def get_networks_for_context(context):
    """Get networks for a specific Docker context."""
    output, err = run_docker_command([
        "docker", "--context", context, "network", "ls", "--format", "{{.Name}}\t{{.Driver}}\t{{.ID}}\t{{.Scope}}"
    ])
    networks = []
    if err:
        return networks, err
    if output:
        for line in output.splitlines():
            try:
                parts = line.split("\t")
                name = parts[0]
                driver = parts[1] if len(parts) > 1 else "N/A"
                network_id = parts[2] if len(parts) > 2 else "N/A"
                scope = parts[3] if len(parts) > 3 else "N/A"
                
                networks.append({
                    "name": name,
                    "driver": driver,
                    "id": network_id,
                    "scope": scope,
                    "context": context
                })
            except ValueError:
                continue
    return networks, ""
