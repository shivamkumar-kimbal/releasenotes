# Number of tags and commits per tag
$tagCount = 5
$commitsPerTag = 5

for ($tag = 1; $tag -le $tagCount; $tag++) {
    for ($commit = 1; $commit -le $commitsPerTag; $commit++) {
        $fileName = "dummy_file_${tag}_${commit}.txt"
        $content = "Dummy content for Tag $tag, Commit $commit"

        # Create a dummy file with content
        Set-Content -Path $fileName -Value $content

        # Stage the file
        git add $fileName

        # Corrected commit message to avoid colon issues by splitting the string
        $commitMessage = "DEVO-19$tag #${commit} for Tag v1.0.$tag" + ": Added ${fileName}"
        git commit -m $commitMessage
        git push
    }

    # Create a tag after each set of 5 commits
    $tagName = "v1.0.$tag"
    git tag $tagName
    Write-Host "🏷️  Created tag $tagName with $commitsPerTag commits."
}

Write-Host "✅ All $tagCount tags created successfully with $commitsPerTag commits each!"
