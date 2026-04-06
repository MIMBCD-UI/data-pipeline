# Zenodo Integration

This repository is integrated with [Zenodo](https://zenodo.org/), a research data repository that allows you to preserve and share research outputs with a permanent Digital Object Identifier (DOI).

## What is Zenodo?

Zenodo is a general-purpose open-access repository developed under the European OpenAIRE program and operated by CERN. It allows researchers to deposit research papers, data sets, software, reports, and any other research-related digital artifacts.

## How It Works

The `.zenodo.json` file in the root of this repository contains metadata about the project. When you create a new release on GitHub, Zenodo automatically:

1. Creates a snapshot of the repository at that release
2. Assigns a unique DOI to that version
3. Makes it citable and discoverable
4. Preserves it for long-term access

## Getting Started with Zenodo

### 1. Enable Zenodo Integration

1. Go to [Zenodo](https://zenodo.org/) and log in with your GitHub account
2. Navigate to the [GitHub integration page](https://zenodo.org/account/settings/github/)
3. Find the `MIMBCD-UI/data-pipeline` repository
4. Enable the toggle to activate automatic preservation

### 2. Create a Release

Once Zenodo integration is enabled:

1. Go to the [GitHub releases page](https://github.com/MIMBCD-UI/data-pipeline/releases)
2. Click "Draft a new release"
3. Create a tag (e.g., `v1.0.0`)
4. Add release notes
5. Publish the release

### 3. Get Your DOI

After publishing the release:

1. Zenodo will automatically create a new version
2. You'll receive a unique DOI for that release
3. Update the DOI badge in `README.md` with your actual DOI

## Updating the DOI Badge

Once you have your DOI from Zenodo, update the badge in `README.md`:

Replace:
```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

With:
```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.YOUR_DOI.svg)](https://doi.org/10.5281/zenodo.YOUR_DOI)
```

Where `YOUR_DOI` is the actual DOI number assigned by Zenodo.

## Metadata

The `.zenodo.json` file contains comprehensive metadata about this project:

- **Title**: MIMBCD-UI Data Pipeline
- **Description**: Information about the data pipeline functionality
- **Creators**: List of authors and their affiliations
- **License**: MIT License
- **Keywords**: Relevant keywords for discoverability
- **Related Identifiers**: Links to related publications and resources
- **Grants**: Funding information

## Benefits

- **Permanent DOI**: Each release gets a unique, permanent identifier
- **Citability**: Others can cite specific versions of your software
- **Preservation**: Long-term archival ensures your work is preserved
- **Discoverability**: Zenodo is indexed by major search engines and research databases
- **Version Control**: Each release is preserved separately with its own DOI

## Citation

Once your DOI is available, others can cite this work using:

```
Calisto, Francisco Maria, Araújo, Diogo, Santiago, Carlos, Barata, Catarina, & Nascimento, Jacinto C. (YEAR). MIMBCD-UI Data Pipeline (Version X.Y.Z) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.YOUR_DOI
```

## More Information

- [Zenodo Help](https://help.zenodo.org/)
- [Making Your Code Citable](https://guides.github.com/activities/citable-code/)
- [Zenodo GitHub Integration](https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content)
