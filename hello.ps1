# Ensure you're in the correct Git repository directory
$commitCount = 10  # Number of dummy commits to create

for ($i = 1; $i -le $commitCount; $i++) {
    $fileName = "dummy_file_$i.txt"
    $content = "Dummy content $i"

    # Create a dummy file with some content
    Set-Content -Path $fileName -Value $content

    # Stage the file
    git add $fileName

    # Use ${} to properly reference variables in the commit message
    git commit -m "Dummy commit #${i}: Added ${fileName}"
    git push
}

# Tag the initial commit before the dummy commits (if not already tagged)
git tag v2.0.0

# Tag the latest commit after the dummy commits
git tag v2.1.0

Write-Host "✅ $commitCount dummy commits created and tagged from v1.0.0 to v1.1.0."
