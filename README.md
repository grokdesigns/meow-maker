<h3 align="center">
	<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/logos/exports/1544x1544_circle.png" width="100" alt="Logo"/><br/>
	<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/misc/transparent.png" height="30" width="0px"/>
	Meow Maker for <a href="https://catppuccin.com/">Catppuccin</a>
	<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/misc/transparent.png" height="30" width="0px"/>
</h3>

<p align="center">
	<a href="https://github.com/grokdesigns/meow-maker/stargazers"><img src="https://img.shields.io/github/stars/grokdesigns/meow-maker?colorA=363a4f&colorB=b7bdf8&style=for-the-badge"></a>
	<a href="https://github.com/grokdesigns/meow-maker/issues"><img src="https://img.shields.io/github/issues/grokdesigns/meow-maker?colorA=363a4f&colorB=f5a97f&style=for-the-badge"></a>
	<a href="https://github.com/grokdesigns/meow-maker/contributors"><img src="https://img.shields.io/github/contributors/grokdesigns/meow-maker?colorA=363a4f&colorB=a6da95&style=for-the-badge"></a>
</p>


## Meow Maker

Meow Maker is a GitHub action that you can add to any repo. After configuration, Meow Maker will run on every push to the repository. Using the input and output folders you configure, all Tera files will be processed by Whiskers and commited back to your repo in the output folder. If you updated your templates and forgot to update your generated files, Meow Maker will take care of it!

## Usage
1. Configure your repository settings to allow actions to read and write to the repo: https://github.com/username/reponame/settings/actions.

<kbd>![image](https://github.com/user-attachments/assets/b902b826-a2f4-4626-aac1-65d3c8fe44af)</kbd>


2. Navigate to the Actions page for your repo: https://github.com/username/reponame/actions/new.

3. Click *Configure* on 'Simple workflow'

4. Using the [example_workflow.yml](example_workflow.yml) file as a template, create your action, gve it a representative name, and commit it to your repo.

5. For testing, you can delete your existing output folder and upon commit, Meow Maker should rebuild the folder and output your files.

## 💝 Thanks to

- [grokdesigns](https://github.com/grokdesigns)

&nbsp;

<p align="center">
	<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/footers/gray0_ctp_on_line.svg?sanitize=true" />
</p>

<p align="center">
	Copyright &copy; 2021-present <a href="https://github.com/catppuccin" target="_blank">Catppuccin Org</a>
</p>

<p align="center">
	<a href="https://github.com/catppuccin/catppuccin/blob/main/LICENSE"><img src="https://img.shields.io/static/v1.svg?style=for-the-badge&label=License&message=MIT&logoColor=d9e0ee&colorA=363a4f&colorB=b7bdf8"/></a>
</p>
