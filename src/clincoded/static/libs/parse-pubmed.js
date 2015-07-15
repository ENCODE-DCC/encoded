'use strict';
// Derived from:
// https://github.com/standard-analytics/pubmed-schema-org/blob/master/lib/pubmed.js

var _ = require('underscore');
var moment = require('moment');

module.exports.parsePubmed = parsePubmed;

/**
 * see http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html
 */
function parsePubmed(xml){
    var article = {};
    var doc = new DOMParser().parseFromString(xml, 'text/xml');

    var $PubmedArticle = doc.getElementsByTagName('PubmedArticle')[0];
    if($PubmedArticle){
        var publicationData = '';

        // Get the PMID
        var $PMID = $PubmedArticle.getElementsByTagName('PMID')[0];
        if($PMID) {
            article.pmid = $PMID.textContent;
        }

        // Get the journal name
        var $Journal = $PubmedArticle.getElementsByTagName('Journal')[0];
        if($Journal){
            article.date = pubmedDatePublished($Journal).toISOString();
            article.date = moment(article.date).format('YYYY-MMM');
            article.journal = pubmedPeriodical($Journal);
        }

        article.firstAuthor = pubmedAuthors($PubmedArticle);

        var $ArticleTitle = $PubmedArticle.getElementsByTagName('ArticleTitle')[0];
        if($ArticleTitle){
            article.title = $ArticleTitle.textContent; //remove [] Cf http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#articletitle
        }

        var abstracts = pubmedAbstract($PubmedArticle);
        if(abstracts){
            article.abstract = abstracts;
        }

        //issue, volume, periodical, all nested...
        if($Journal){

            var publicationIssue = pubmedPublicationIssue($Journal);
            var publicationVolume = pubmedPublicationVolume($Journal);
            var publicationPgn = '';

            //pages (bibo:pages (bibo:pages <-> schema:pagination) or bibo:pageStart and bibo:pageEnd e.g <Pagination> <MedlinePgn>12-9</MedlinePgn>)
            var $Pagination = $PubmedArticle.getElementsByTagName('Pagination')[0];
            if($Pagination){
                var $MedlinePgn = $Pagination.getElementsByTagName('MedlinePgn')[0];
                if($MedlinePgn){
                    publicationPgn = $MedlinePgn.textContent;
                }
            }
            publicationData = publicationVolume + (publicationIssue ? '(' + publicationIssue + ')' : '')  + ':' + publicationPgn;
        }
        if (publicationData) {
            article.date += ';' + publicationData;
        }
    }

    return article;
}

function pubmedAuthors($PubmedArticle){
    var authors = {};
    var firstAuthor = '';

    var $AuthorList = $PubmedArticle.getElementsByTagName('AuthorList')[0];
    if($AuthorList){
        var $Authors = $AuthorList.getElementsByTagName('Author');
        var $FirstAuthor = $Authors[0];

        var $LastName = $FirstAuthor.getElementsByTagName('LastName')[0];
        if($LastName){
            firstAuthor = $LastName.textContent;
        }

        var $Initials = $FirstAuthor.getElementsByTagName('Initials')[0];
        if($Initials){
            firstAuthor += (firstAuthor ? ' ' : '') + $Initials.textContent;
        }
    } else {
        firstAuthor = 'Anonymous';
    }
    return firstAuthor;
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
        return $issue.textContent;
    }
    return '';
}

function pubmedPublicationVolume($Journal){

    var $volume = $Journal.getElementsByTagName('Volume')[0];
    if($volume){
        return $volume.textContent;
    }
    return '';
}

function pubmedPeriodical($Journal){

    var $Title = $Journal.getElementsByTagName('Title')[0];
    if($Title){
        return $Title.textContent;
    }
    return '';

}


/**
 * CF http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html structured abstract.
 * Abstract can be structured
 *e.g http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=19897313&rettype=abstract&retmode=xml
 */

function pubmedAbstract($PubmedArticle){
    var abstractText = '';

    var $Abstracts = $PubmedArticle.getElementsByTagName('Abstract');
    if($Abstracts && $Abstracts.length){

        var $AbstractTexts = $Abstracts[0].getElementsByTagName('AbstractText');
        if($AbstractTexts && $AbstractTexts.length){

            abstractText = $AbstractTexts[0].textContent;

        }

    }
    return abstractText;

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
