# -*- coding: utf-8 -*-
# WebService for JobCrawler - Vr.: 1.0
import json
from itertools import groupby

from flask import Flask
from flask import render_template
from flask import request
from nltk.corpus import stopwords

import db_utils
from custom_libs.job_scraper import clean_title

stop_words = set(stopwords.words("portuguese"))

# -------------------- #
# Flask Initialization #
# -------------------- #
app = Flask(__name__)
app.debug = False
app.config.from_object(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/graphs')
def graphs():
    return render_template('graficos.html')


@app.route('/graph1')
def graphs1():
    result = db_utils.execute_query(
        """MATCH (n:LANGUAGE)-[r]-(j:JOB) RETURN n.nid AS lang, COUNT(r) AS count ORDER BY count DESC LIMIT 10;"""
    )
    result = result.data()
    labels = list()
    values = list()

    for r in result:
        labels.append(r['lang'])
        values.append(r['count'])

    data = {
        'labels': labels,
        'values': values
    }
    return json.dumps(data)


@app.route('/graph2')
def graphs2():
    result = db_utils.execute_query(
        """MATCH (n:DATABASES)-[r]-(j:JOB) RETURN n.nid AS lang, COUNT(r) AS count ORDER BY count DESC LIMIT 10;"""
    )
    result = result.data()
    labels = list()
    values = list()

    for r in result:
        labels.append(r['lang'])
        values.append(r['count'])

    data = {
        'labels': labels,
        'values': values
    }
    return json.dumps(data)


@app.route('/graph3', methods=['POST', 'GET'])
def graphs3():
    if request.method == 'GET':
        terms = ['python', 'java', 'sql', 'javascript', 'nosql', 'c']
    else:
        terms = json.loads(request.data)

    frag = ""
    for i, t in enumerate(terms):
        frag += "t.nid='%s' " % t
        if i + 1 != len(terms):
            frag += 'OR '
    q = """
        MATCH (t:TechTerm)-[r1]-(v:JOB)-[r2]-(f:SalaryRange) 
        WHERE 
            %s 
        RETURN t.nid, f.nid, f.value, COUNT(v.nid) AS count ORDER BY t.nid, toInt(f.value);
        """ % frag
    result = db_utils.execute_query(q)
    result = result.data()

    if len(result) == 0:
        return json.dumps({'result': True, 'message': "Nenhum termo foi encontrado"})

    terms = [term for term in terms if term in [r['t.nid'] for r in result]]

    labels = list()
    for it in result:
        it['f.value'] = int(it['f.value'])
    [labels.append(it['f.nid']) for it in sorted(result, key=lambda k: k['f.value']) if it['f.nid'] not in labels]

    terms_info = dict()
    for term in {it['t.nid'] for it in result}:
        terms_info[term] = {
            'range': [it['f.nid'] for it in result if it['t.nid'] == term],
            'seq': list()
        }

        for label in labels:
            if label in terms_info[term]['range']:
                terms_info[term]['seq'].append(
                    [r for r in result if r['t.nid'] == term and r['f.nid'] == label][0]['count']
                )
            else:
                terms_info[term]['seq'].append(None)

    order = list()
    for t in terms:
        order.append(terms_info[t]['seq'])
        # print t, terms_info[t]['seq'], sum(terms_info[t]['seq'])

    return_data = {
        'labels': [lb.split('_')[-1] for lb in labels],
        'series': order,
        'terms': terms
    }

    return json.dumps({'result': True, 'data': return_data})


@app.route('/relacoes', methods=["GET", "POST"])
def relacoes():
    try:
        if request.method == 'GET':
            return render_template('relacoes.html', termos=['Nenhum :-('],
                                   results=[], length='Sem termos de busca, sem ')
        else:
            terms = sorted(set([request.form[t].strip().lower() for t in request.form if request.form[t] != '']))
            if len(terms) == 0:
                return render_template('relacoes.html', termos=['Nenhum :-('], results=[])
            else:
                results = list()
                not_found = list()
                for r in terms:
                    requirements_rel = db_utils.search_requirements(r)
                    if requirements_rel is not None and requirements_rel:
                        results.append({
                            'term': r,
                            'list': sorted(requirements_rel, key=lambda k: k['count'])
                        })
                    else:
                        not_found.append(r)

                all_terms = list()
                for it in [d['list'] for d in results]:
                    for i in it:
                        all_terms.append(i['nid'])
                all_terms = sorted(all_terms)
                number_terms = {key: len(list(group)) for (key, group) in groupby(all_terms)}

                matches_needed = set()

                for i, it in enumerate(results):
                    for _ in [n['nid'] for n in it['list']]:
                        for item in results[i]['list']:
                            item['avg'] = db_utils.avg_salary_with_two_terms(it['term'], item['nid'])
                            if number_terms[item['nid']] > 1 and item['nid'] not in terms:
                                item['strong'] = True
                                matches_needed.add(item['nid'])
                            else:
                                item['strong'] = False
                    clean_avg = [a for a in [item['avg'] for item in results[i]['list']] if a]
                    it['avg'] = int(sum(clean_avg)) / len(clean_avg)

                for i, it in enumerate(results):
                    for _ in [n['nid'] for n in it['list']]:
                        for item in results[i]['list']:
                            if item['strong'] and item['avg'] >= it['avg']:
                                item['special'] = True
                            else:
                                item['special'] = False

                return render_template('relacoes.html', termos=terms, results=results,
                                       not_found=not_found, match_needed=sorted(matches_needed))
    except Exception as err:
        return str(err)


@app.route("/busca", methods=["POST"])
def busca():
    try:
        raw_text = request.form.get("searchText", "").strip()
        search_terms = sorted({w.lower() for w in raw_text.split() if w.strip()})

        if not search_terms:
            return render_template(
                "resultados.html",
                termos=["Nenhum :-("],
                results=[],
                length="Sem termos de busca, sem ",
            )

        records = db_utils.search_jobs(search_terms)

        results = []
        for record in records:
            data = record.data() if hasattr(record, "data") else record

            description = data.get("description", "") or ""
            lines_content = description.split("\n")
            fixed_lines = [
                " ".join([f for f in line.split(" ") if len(f) < 60])
                for line in lines_content
            ]

            results.append({
                "site": (data.get("site", "") or "").replace("/", " / "),
                "compatibility": f"{int(data.get('match_rate', 0) * 100)}%",
                "sort_value": data.get("match_rate", 0),
                "link": data.get("link", "") or "",
                "salary": data.get("salary", "") or "",
                "matches": sorted(data.get("matches", [])),
                "desc": clean_title(
                    " - ".join(fixed_lines)[:350].replace("\\", " ")
                ) + " . . .",
            })

        return render_template(
            "resultados.html",
            termos=search_terms,
            results=results,
            length=len(results),
        )

    except Exception as err:
        return str(err)


if __name__ == '__main__':
    try:
        app.run('localhost', threaded=True)
    except Exception as ex:
        print(ex)
