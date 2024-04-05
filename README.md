<meta http-equiv="refresh" content="0; url='https://mimbcd-ui.github.io/data-pipeline/web/index.html'" />

# Data Pipeline

<img src="https://github.com/MIMBCD-UI/data-pipeline/blob/master/assets/diagram.png?raw=true" width="100%" />

[![License](https://img.shields.io/badge/License-Academic%20%2B%20Commercial-blue?style=flat-square)](https://github.com/MIMBCD-UI/data-pipeline/blob/master/LICENSE.md)
[![Last commit](https://img.shields.io/github/last-commit/MIMBCD-UI/data-pipeline?style=flat-square)](https://github.com/MIMBCD-UI/data-pipeline/commits/master)
[![OpenCollective](https://opencollective.com/oppr/backers/badge.svg?style=flat-square)](#backers)
[![OpenCollective](https://opencollective.com/oppr/sponsors/badge.svg?style=flat-square)](#sponsors)
[![Gitter](https://img.shields.io/gitter/room/gitterHQ/gitter.svg?style=flat-square)](https://gitter.im/opprTeam)
[![Twitter](https://flat.badgen.net/badge/icon/twitter?icon=twitter&label)](https://twitter.com/opprGroup)

This repository contains a data pipeline for processing medical imaging data. It includes modules for anonymizing DICOM files, encrypting patient IDs, extracting metadata, and processing the data.

## Modules

- `anonymizer.py`: Module for anonymizing DICOM files by removing patient-related information and renaming them according to a specified format.
- `encryption.py`: Module for encrypting patient IDs.
- `extractor.py`: Module for extracting metadata from DICOM files.
- `main.py`: Main script for executing the data processing pipeline.
- `processor.py`: Module for processing medical imaging data.

## Usage

To use the data pipeline, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/MIMBCD-UI/data-pipeline.git
```

2. Install the required dependencies by creating a virtual environment and installing the packages listed in `requirements.txt`:

```bash
cd data-pipeline
pip install -r requirements.txt
```

3. Run the main script to execute the data processing pipeline:

```bash
python main.py
```

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please fork the repository and submit a pull request with your proposed changes.

## License

This project is licensed under the [MIT License](LICENSE).

### Team

Our team brings everything together sharing ideas and the same purpose, developing even better work. In this section, we will nominate the full list of important people for this repository, as well as respective links.

#### Authors

* Francisco Maria Calisto [ [Academic Website](https://web.tecnico.ulisboa.pt/francisco.calisto) | [ResearchGate](https://www.researchgate.net/profile/Francisco_Maria_Calisto) | [GitHub](https://github.com/FMCalisto) | [Twitter](https://twitter.com/FMCalisto) | [LinkedIn](https://www.linkedin.com/in/fmcalisto/) ]

* Diogo Araújo

* Carlos Santiago [ [ResearchGate](https://www.researchgate.net/profile/Carlos-Santiago-4) ]

* Catarina Barata

* Jacinto C. Nascimento [ [ResearchGate](https://www.researchgate.net/profile/Jacinto_Nascimento) ]

#### Promoters

* João Fernandes [ [ResearchGate](https://www.researchgate.net/profile/Joao-Fernandes-102) ]

* Margarida Morais [ [ResearchGate](https://www.researchgate.net/profile/Margarida_Morais2) ]

* João Maria Abrantes [ [ResearchGate](https://www.researchgate.net/profile/Joao-Abrantes-2) ]

* Nuno Nunes [ [ResearchGate](https://www.researchgate.net/profile/Nuno_Nunes2) ]

#### Companions

* Hugo Lencastre
* Nádia Mourão
* Miguel Bastos
* Pedro Diogo
* João Bernardo
* Madalena Pedreira
* Mauro Machado
* Bruno Dias
* Bruno Oliveira
* Luís Ribeiro Gomes

#### Acknowledgements

This work was partially supported by national funds by [FCT](http://fct.pt/) through both UID/EEA/50009/2013 and LARSyS - FCT Project 2022.04485.PTDC (MIA-BREAST) projects hosted by [IST](http://tecnico.ulisboa.pt/), as well as both BL89/2017-IST-ID and PD/BD/150629/2020 grants. We are indebted to those who gave their time and expertise to evaluate our work, who among others are giving us crucial information for the [BreastScreening](https://github.com/BreastScreening) project.

### Supporting

Our organization is a non-profit organization. However, we have many needs across our activity. From infrastructure to service needs, we need some time and contribution, as well as help, to support our team and projects.

<span>
  <a href="https://opencollective.com/oppr" target="_blank">
    <img src="https://opencollective.com/oppr/tiers/backer.svg" width="220">
  </a>
</span>

#### Contributors

This project exists thanks to all the people who contribute. [[Contribute](CONTRIBUTING.md)].

<span class="image">
  <a href="graphs/contributors">
    <img src="https://opencollective.com/oppr/contributors.svg?width=890" />
  </a>
</span>

#### Backers

Thank you to all our backers! 🙏 [[Become a backer](https://opencollective.com/oppr#backer)]

<span>
  <a href="https://opencollective.com/oppr#backers" target="_blank">
    <img src="https://opencollective.com/oppr/backers.svg?width=890">
  </a>
</span>

#### Sponsors

Support this project by becoming a sponsor. Your logo will show up here with a link to your website. [[Become a sponsor](https://opencollective.com/oppr#sponsor)]

<span>
  <a href="https://opencollective.com/oppr/sponsor/0/website" target="_blank">
    <img src="https://opencollective.com/oppr/sponsor/0/avatar.svg">
  </a>
</span>

<br />

<span>
  <a href="http://www.fct.pt/" title="FCT" target="_blank">
    <img src="https://github.com/mida-project/meta/blob/master/brands/fct_footer.png?raw=true" alt="fct" width="20%" />
  </a>
</span>
<span>
  <a href="https://www.fccn.pt/en/" title="FCCN" target="_blank">
    <img src="https://github.com/mida-project/meta/blob/master/brands/fccn_footer.png?raw=true" alt="fccn" width="20%" />
  </a>
</span>
<span>
  <a href="https://www.ulisboa.pt/en/" title="ULisboa" target="_blank">
    <img src="https://github.com/mida-project/meta/blob/master/brands/ulisboa_footer.png?raw=true" alt="ulisboa" width="20%" />
  </a>
</span>
<span>
  <a href="http://tecnico.ulisboa.pt/" title="IST" target="_blank">
    <img src="https://github.com/mida-project/meta/blob/master/brands/ist_footer.png?raw=true" alt="ist" width="20%" />
  </a>
</span>
<span>
  <a href="http://hff.min-saude.pt/" title="HFF" target="_blank">
    <img src="https://github.com/mida-project/meta/blob/master/brands/hff_footer.png?raw=true" alt="hff" width="20%" />
  </a>
</span>
<span>
  <a href="https://www.chtmad.min-saude.pt/" title="CHTMAD" target="_blank">
    <img src="https://raw.githubusercontent.com/MIMBCD-UI/meta/master/brands/chtmad_footer.png" alt="chtmad" width="10%" />
  </a>
</span>

##### Departments

<span>
  <a href="http://dei.tecnico.ulisboa.pt" title="DEI" target="_blank">
    <img src="https://github.com/mida-project/meta/blob/master/brands/dei_footer.png?raw=true" alt="dei" width="20%" />
  </a>
</span>
<span>
  <a href="http://deec.tecnico.ulisboa.pt" title="DEEC" target="_blank">
    <img src="https://github.com/mida-project/meta/blob/master/brands/deec_footer.png?raw=true" alt="dei" width="20%" />
  </a>
</span>

##### Laboratories

<span>
  <a href="http://sipg.isr.tecnico.ulisboa.pt/" title="SIPG" target="_blank">
    <img src="https://github.com/mida-project/meta/blob/master/brands/sipg_footer.png?raw=true" alt="sipg" width="20%" />
  </a>
</span>
<span>
  <a href="http://welcome.isr.tecnico.ulisboa.pt/" title="ISR" target="_blank">
    <img src="https://github.com/mida-project/meta/blob/master/brands/isr-lisboa_footer.png?raw=true" alt="isr" width="20%" />
  </a>
</span>
<span>
  <a href="http://larsys.pt/" title="LARSys" target="_blank">
    <img src="https://github.com/mida-project/meta/blob/master/brands/larsys_footer.png?raw=true" alt="larsys" width="20%" />
  </a>
</span>
<span>
  <a href="https://iti.larsys.pt/" title="ITI" target="_blank">
    <img src="https://github.com/mida-project/meta/blob/master/brands/iti_footer.png?raw=true" alt="iti" width="20%" />
  </a>
</span>
<span>
  <a href="http://www.inesc-id.pt/" title="INESC-ID" target="_blank">
    <img src="https://github.com/mida-project/meta/blob/master/brands/inesc-id_footer.png?raw=true" alt="inesc-id" width="20%" />
  </a>
</span>

##### Domain

<span>
  <a href="https://europa.eu/" title="EU" target="_blank">
    <img src="https://github.com/mida-project/meta/blob/master/brands/eu_footer.png?raw=true" alt="eu" width="20%" />
  </a>
</span>
<span>
  <a href="https://www.portugal.gov.pt/" title="Portugal" target="_blank">
    <img src="https://github.com/mida-project/meta/blob/master/brands/pt_footer.png?raw=true" alt="pt" width="20%" />
  </a>
</span>