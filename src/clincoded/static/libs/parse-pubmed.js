'use strict';
// Derived from:
// https://github.com/standard-analytics/pubmed-schema-org/blob/master/lib/pubmed.js

var _ = require('underscore');

module.exports.parsePubmed = parsePubmed;

/**
 * see http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html
 */
function parsePubmed(xml, pmid){
    var pkg;
    var doc = new DOMParser().parseFromString(xml, 'text/xml');

    var $PubmedArticle = doc.getElementsByTagName('PubmedArticle')[0];
    if($PubmedArticle){

        var $Journal = $PubmedArticle.getElementsByTagName('Journal')[0];
        var jsDate, periodical;
        if($Journal){
            jsDate = pubmedDatePublished($Journal);
            periodical = pubmedPeriodical($Journal);
        }
        var authors = pubmedAuthors($PubmedArticle);

        var pkgId = [];

        if(periodical && periodical.alternateName){
            pkgId.push(periodical.alternateName.toLowerCase());
        }

        if(authors.author && authors.author.familyName){
            pkgId.push(authors.author.familyName.toLowerCase());
        }

        if(jsDate){
            pkgId.push(jsDate.getFullYear());
        }

        if(pkgId.length>=2){
            pkgId = pkgId.join('-');
        } else {
            pkgId = pmid.toString();
        }

        pkg = {
            '@context': '',
            '@id': pkgId,
            '@type': 'MedicalScholarlyArticle'
        };
        pkg.version = '0.0.0';

        var sameAs = ['http://www.ncbi.nlm.nih.gov/pubmed/' + pmid];
        var doi = pubmedDoi($PubmedArticle);
        if (doi) { sameAs.push('http://doi.org/' + doi); }


        var keywords = pubmedKeywords($PubmedArticle);
        if(keywords){
            pkg.keywords = keywords;
        }

        if(jsDate){ pkg.datePublished = jsDate.toISOString(); }

        var $ArticleTitle = $PubmedArticle.getElementsByTagName('ArticleTitle')[0];
        if($ArticleTitle){
            pkg.headline = $ArticleTitle.textContent; //remove [] Cf http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#articletitle
        }

        if(authors.author){ pkg.author = authors.author; }
        if(authors.contributor){ pkg.contributor = authors.contributor; }

        var $CopyrightInformation = $PubmedArticle.getElementsByTagName('CopyrightInformation')[0];
        if($CopyrightInformation){
            pkg.copyrightHolder = { description: $CopyrightInformation.textContent };
        }

        pkg.provider = {
            '@type': 'Organization',
            '@id': 'http://www.ncbi.nlm.nih.gov/pubmed/',
            description: 'From MEDLINE®/PubMed®, a database of the U.S. National Library of Medicine.'
        };

        var sourceOrganization = pubmedSourceOrganization($PubmedArticle);
        if(sourceOrganization){
            pkg.sourceOrganization = sourceOrganization;
        }

        var abstracts = pubmedAbstract($PubmedArticle);
        if(abstracts){
            pkg.abstract = abstracts;
        }

        //issue, volume, periodical, all nested...
        if($Journal){
            var isPartOf;

            var publicationIssue = pubmedPublicationIssue($Journal);
            if(publicationIssue){
                isPartOf = publicationIssue;
            }

            var publicationVolume = pubmedPublicationVolume($Journal);
            if(publicationVolume){
                if(publicationIssue){
                    publicationIssue.isPartOf = publicationVolume;
                } else {
                    isPartOf = publicationVolume;
                }
            }

            if(periodical){
                if(publicationVolume){
                    publicationVolume.isPartOf = periodical;
                } else if (publicationIssue){
                    publicationIssue.isPartOf = periodical;
                } else {
                    isPartOf = periodical;
                }
            }

            if(isPartOf){ pkg.isPartOf = isPartOf; }

            //pages (bibo:pages (bibo:pages <-> schema:pagination) or bibo:pageStart and bibo:pageEnd e.g <Pagination> <MedlinePgn>12-9</MedlinePgn>)
            var $Pagination = $PubmedArticle.getElementsByTagName('Pagination')[0];
            if($Pagination){
                var $MedlinePgn = $Pagination.getElementsByTagName('MedlinePgn')[0];
                if($MedlinePgn){
                    var medlinePgn = $MedlinePgn.textContent || '';
                    var rePage = /^(\d+)-(\d+)$/;
                    var matchPage = medlinePgn.match(rePage);
                    if(matchPage){ //fix ranges like 1199-201 or 12-9
                        var pageStart = matchPage[1];
                        var pageEnd = matchPage[2];
                        if(pageEnd.length < pageStart.length){
                            pageEnd = pageStart.substring(0, pageStart.length - pageEnd.length) + pageEnd;
                        }
                        pkg.pageStart = parseInt(pageStart, 10);
                        pkg.pageEnd = parseInt(pageEnd, 10);
                    } else {
                        pkg.pagination = medlinePgn;
                    }
                }
            }
        }
    }

    return pkg;
}

function pubmedAuthors($PubmedArticle){
    var authors = {};

    var $AuthorList = $PubmedArticle.getElementsByTagName('AuthorList')[0];
    if($AuthorList){
        var $Authors = $AuthorList.getElementsByTagName('Author');
        if($Authors){
            Array.prototype.forEach.call($Authors, function($Author, i){
                var person = { '@type': 'Person' };

                var $LastName = $Author.getElementsByTagName('LastName')[0];
                if($LastName){
                    person.familyName = $LastName.textContent;
                }

                var $ForeName = $Author.getElementsByTagName('ForeName')[0];
                if($ForeName){
                    person.givenName = $ForeName.textContent;
                }

                if(person.familyName && person.givenName ){
                    person.name = person.givenName + ' ' + person.familyName;
                }

                var $Affiliation = $Author.getElementsByTagName('Affiliation')[0];
                if($Affiliation){
                    person.affiliation = {
                        '@type': 'Organization',
                        description: $Affiliation.textContent
                    };
                }

                if(Object.keys(person).length > 1){
                    if(i === 0){
                        authors.author = person;
                    } else {
                        if(!authors.contributor){
                            authors.contributor = [];
                        }
                        authors.contributor.push(person);
                    }
                }

            });
        }
    }
    return authors;
}

function pubmedDoi($PubmedArticle){
    var $ELocationID = $PubmedArticle.getElementsByTagName('ELocationID');
    if($ELocationID){
        for(var i=0; i<$ELocationID.length; i++){
            if($ELocationID[i].getAttribute('EIdType') === 'doi'){
                var doiValid = $ELocationID[i].getAttribute('ValidYN');
                if(!doiValid || doiValid === 'Y'){
                    return $ELocationID[i].textContent;
                }
            }
        }
    }
}


function pubmedDatePublished($Journal){
    var $PubDate = $Journal.getElementsByTagName('PubDate')[0];
    if($PubDate){
        var $day = $PubDate.getElementsByTagName('Day')[0];
        var $month = $PubDate.getElementsByTagName('Month')[0];
        var $year = $PubDate.getElementsByTagName('Year')[0];
        var month, jsDate;

        if($month){
            var abrMonth2int = {
                'jan': 0,
                'feb': 1,
                'mar': 2,
                'apr': 3,
                'may': 4,
                'jun': 5,
                'july': 6,
                'aug': 7,
                'sep': 8,
                'oct': 9,
                'nov': 10,
                'dec': 11
            };

            month = abrMonth2int[$month.textContent.trim().toLowerCase()];
        }

        if($year && month && $day){
            jsDate = Date.UTC($year.textContent, month, $day.textContent, 0, 0, 0, 0);
        } else if($year && month){
            jsDate = Date.UTC($year.textContent, month, 1, 0, 0, 0, 0);
        } else if($year){
            jsDate = Date.UTC($year.textContent, 0, 1, 0, 0, 0, 0);
        }

        if(jsDate){
            jsDate = new Date(jsDate - 1000*5*60*60); //UTC to Eastern Time Zone (UTC-05:00)
        } else {
            var $MedlineDate = $PubDate.getElementsByTagName('MedlineDate')[0];
            if($MedlineDate){
                try {
                    jsDate = new Date($MedlineDate.textContent);
                } catch(e){}
            }
        }
        if(jsDate){
            return jsDate;
        }
    }
}

function pubmedPublicationIssue($Journal){

    var $issue = $Journal.getElementsByTagName('Issue')[0];
    if($issue){
        return {
            '@type': 'PublicationIssue',
            issueNumber: parseInt($issue.textContent, 10)
        };
    }

}

function pubmedPublicationVolume($Journal){

    var $volume = $Journal.getElementsByTagName('Volume')[0];
    if($volume){
        return {
            '@type': 'PublicationVolume',
            volumeNumber: parseInt($volume.textContent, 10)
        };
    }

}

function pubmedPeriodical($Journal){

    var periodical = { '@type': 'Periodical' };

    var $Title = $Journal.getElementsByTagName('Title')[0];
    if($Title){
        periodical.name = $Title.textContent;
    }

    var $ISOAbbreviation = $Journal.getElementsByTagName('ISOAbbreviation')[0];
    if($ISOAbbreviation){
        periodical.alternateName = $ISOAbbreviation.textContent;
    }

    var $ISSN = $Journal.getElementsByTagName('ISSN')[0];
    if($ISSN){
        periodical.issn = $ISSN.textContent;
    }

    if(Object.keys(periodical).length > 1){
        return periodical;
    }

}


/**
 * CF http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html structured abstract.
 * Abstract can be structured
 *e.g http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=19897313&rettype=abstract&retmode=xml
 */

function pubmedAbstract($PubmedArticle){

    var $Abstracts = $PubmedArticle.getElementsByTagName('Abstract');
    if($Abstracts && $Abstracts.length){

        return Array.prototype.map.call($Abstracts, function($Abstract){

            var myAbstract = { '@type': 'Abstract' };

            var $AbstractTexts = $Abstract.getElementsByTagName('AbstractText');
            if($AbstractTexts && $AbstractTexts.length){

                var parts = Array.prototype.map.call($AbstractTexts, function($AbstractText){
                    var part = { '@type': 'Abstract' };
                    var nlmCategory = $AbstractText.getAttribute('NlmCategory') || $AbstractText.getAttribute('Label');
                    if(nlmCategory){
                        part.headline = nlmCategory.trim().toLowerCase();
                    }
                    part.abstractBody = $AbstractText.textContent;
                    return part;
                });

                if(parts.length === 1){
                    if(parts[0].headline){
                        myAbstract.headline = parts[0].headline;
                    }
                    myAbstract.abstractBody = parts[0].abstractBody;
                } else {
                    myAbstract.hasPart = parts;
                }

            }

            return myAbstract;

        });

    }

}


/**
 * keywords e.g http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=24920540&rettype=abstract&retmode=xml
 * TODO: take advandage of Owner attribute Cf http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#Keyword
 */
function pubmedKeywords($PubmedArticle){

    var keywords = [];
    var $KeywordLists = $PubmedArticle.getElementsByTagName('KeywordList');
    if($KeywordLists){
        Array.prototype.forEach.call($KeywordLists, function($KeywordList){
            var $Keywords = $KeywordList.getElementsByTagName('Keyword');
            if($Keywords){
                Array.prototype.forEach.call($Keywords, function($Keyword){
                    keywords.push($Keyword.textContent).toLowerCase();
                });
            }
        });
    }

    if(keywords.length){
        return _.uniq(keywords);
    }

}



/**
 * <Grant> as sourceOrganization (grantId is added TODO fix...)
 */
function pubmedSourceOrganization($PubmedArticle){

    var $GrantList = $PubmedArticle.getElementsByTagName('GrantList')[0];
    var soMap = {}; //re-aggregate grant entries by organizations
    if($GrantList){
        var $Grants = $GrantList.getElementsByTagName('Grant');
        if($Grants){
            Array.prototype.forEach.call($Grants, function($Grant, gid){
                var $Agency = $Grant.getElementsByTagName('Agency')[0];
                var $GrantID = $Grant.getElementsByTagName('GrantID')[0];
                var $Acronym = $Grant.getElementsByTagName('Acronym')[0];
                var $Country = $Grant.getElementsByTagName('Country')[0];

                var name;
                if($Agency){
                    name = $Agency.textContent;
                }

                var key = name || gid.toString();

                if($Agency || $GrantID){
                    var organization = soMap[key] || { '@type': 'Organization' };
                    if(name){
                        organization.name = name;
                    }
                    if($Acronym){
                        organization.alternateName = $Acronym.textContent;
                    }
                    if($GrantID){ //accumulate grantId(s)...
                        var grantId = $GrantID.textContent;
                        if(organization.grantId){
                            organization.grantId.push(grantId);
                        } else {
                            organization.grantId = [grantId];
                        }
                    }
                    if($Country){
                        organization.address = {
                            '@type': 'PostalAddress',
                            'addressCountry': $Country.textContent
                        };
                    }
                    soMap[key] = organization;
                }
            });
        }
    }

    var sourceOrganizations = [];
    Object.keys(soMap).forEach(function(key){
        sourceOrganizations.push(soMap[key]);
    });

    if(sourceOrganizations.length){
        return sourceOrganizations;
    }


}
