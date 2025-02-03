# Creating a GitHub Personal Access Token

Follow these steps to create a personal access token for GitHub:

1. **Sign in to GitHub**
   - Go to https://github.com and sign in to your account

2. **Access Token Settings**
   - Click on your profile picture in the top-right corner
   - Select "Settings" from the dropdown menu
   - Scroll down to "Developer settings" in the left sidebar
   - Click on "Personal access tokens"
   - Select "Tokens (classic)"

3. **Generate New Token**
   - Click "Generate new token"
   - Select "Generate new token (classic)"
   - You might need to confirm your password

4. **Configure Token**
   - Name: "ad-agent-repo" (or any descriptive name)
   - Set expiration: Choose an appropriate duration
   - Select scopes:
     - ✓ `repo` (Full control of private repositories)
     - This includes:
       - repo:status
       - repo_deployment
       - public_repo
       - repo:invite
       - security_events

5. **Generate and Copy Token**
   - Scroll to the bottom and click "Generate token"
   - **IMPORTANT**: Copy the token immediately! You won't be able to see it again.
   - Store it securely as we'll need it to set up the GitHub MCP server

Once you have your token, please provide it to me, and I'll help you set up the GitHub MCP server to create and manage your private repository.

Note: Keep your token secure and never share it publicly. Treat it like a password.
