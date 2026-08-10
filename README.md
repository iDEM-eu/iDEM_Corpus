# The iDEM_Corpus

The iDEM Corpus was created as a part of the [iDEM project](https://idemproject.eu/). 
It is a corpus of high quality text simplifications which covers
Italian, Catalan, and Spanish. The corpus was presented and described in [A Multilingual Human Annotated Corpus of Original and Easy-to-Read Texts to Support Access to Democratic Participatory Processes](https://aclanthology.org/2026.lrec-1.87/) (Bott et al., LREC 2026)

## The corpus contains:
* Original Texts
* Simplified Text
* Annotations on which simplification strategies have been applied when producing the simplified text (this part is still
under revision and still not published here)

The sizes of the language-specific parts in sentences and words are as follows:


<table>
    <tr>
        <th>Language</th>
        <th colspan="2"> Sentences</th>
        <th colspan="2"> Sentences</th>
        <th colspan="2"> Words per Sentence Segement </th>
    </tr>
    <tr>
        <th></th>
        <th>  Orig      </th>
        <th> Simp  </th>
        <th> Orig  </th>
        <th> Simp  </th>
        <th> Orig  </th>
        <th>  Simp </th>
    </tr>
    <tr>
        <th> Spanish </th>
        <th>  354  </th>
        <th> 1290  </th>
        <th> 11665 </th>
        <th>10883  </th>
        <th> 32.95 </th>
        <th>  8.44 </th>
    </tr>
    <tr> 
        <th> Catalan  </th>
        <th>  380 </th>
        <th>  405  </th>
        <th> 11570 </th>
        <th> 14279 </th>
        <th> 41.32 </th>
        <th> 35.26 </tr>
    </tr>
    <tr>
        <th> Italian </th>
        <th>  325  </th>
        <th>  718  </th>
        <th> 10398 </th>
        <th> 12230 </th>
        <th> 31.99 </th>
        <th> 17.03 </th>
    </tr>
</table>
The corpus contains texts from the domain of public deliberation from different sources, like informative texts from institutions, political articles, and news articles, among others. In terms of content, it covers social policy, justice and services, health policy, accessibility, governance and similar topics.

The simplified versions of the texts were produced by professional E2R translators, on the basis of variants of three language-specific versions of the E2R recommendations. While translating, translators annotated which E2R recommendations they were applying. The recommendations varied somewhat across languages, but targeted the same linguistic phenomena. 

The corpus was used as test data in the 
[IberLef/MerTrans shared task](https://lastus-taln-upf.github.io/mertrans-iberlef-2026/). The version used there can be found in the folder 'IberLef-MerTrans-Version' 

## Cite: 

@inproceedings{Bott&al2026,
  author    = {Bott, Stefan and Riegler, Verena and Saggion, Horacio and Rasc{\'o}n-Alcaina, Almudena and Khallaf, Nouran},
  title     = {A Multilingual Human Annotated Corpus of Original and Easy-to-Read Texts to Support Access to Democratic Participatory Processes},
  booktitle = {Proceedings of the Language Resources and Evaluation Conference 2026 (LREC 2026)},
  year      = {2026},
  address   = {Palma, Mallorca, Spain}
}

### To cite the MerTrans/IberLef version:

@inproceedings{mertrans,
    author = "Horacio Saggion, Mehrzad Tareh, Nouran Khallaf, Stefan Bott, Daniel Adanza, Almudena Rascón Alcaina, Nelson Pérez Rojas, Sandra Szasz",
    title = "Overview of MER-TRANS at IberLEF 2026: First Shared Task on Multilingual Easy-to-Read Translation",
  booktitle={Proceedings of the Iberian Languages Evaluation Forum (IberLEF 2026), co-located with the 42nd Conference of the Spanish Society for Natural Language Processing (SEPLN 2026), CEUR-WS.org},
  year={2026}
}
