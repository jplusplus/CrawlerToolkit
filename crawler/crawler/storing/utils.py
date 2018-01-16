def as_hosted_content(content, resources):
    """
    Produce suitabled "hosted" version of a text file.
    It can remplace a list of URLs based on dict map.
    """
    def multiple_replace(txt, _dict):
        rx = re.compile('|'.join(map(re.escape, _dict)))
        def one_xlat(match):
            return _dict[match.group(0)]
        return rx.sub(one_xlat, txt)

    content = content.decode()
    if len(resources) > 0:
        mapped_urls = {
            resource['url']: mediaurl(resource['hosted_url']) for resource in resources
        }
        content = multiple_replace(content, mapped_urls)
    return bytes(content, 'utf-8')

def process_css(css, resources):
    """
    Parse given CSS file & identify subresources (fonts mostly)
    """
    content = css['content']
    resources_dict = resources[css['url']]
    resources_list = list()
    for rtype, sub_resources in resources_dict.items():
        sub_resources_list += map(
            lambda res: save_resource(article, res, rtype=rtype),
            sub_resources
        )
    return as_hosted_content(content, resources_list)

def save_resource(article, resource, use_tdir=True, uniq_fn=True):
    fn = resource['filename']
    content = resource['content']
    path = article.resource_path(fn, use_tdir=use_tdir, uniq_fn=uniq_fn)
    f = storage.open(path)
    f.write(content)
    f.close()
    resource['hosted_url'] = path
    return resource

def save_resources(article, resources_dict, css_resources):
    article_resources = list()
    for ressource_type, resources in resources_dict.items():
        for resource_dict in resources:
            if rtype == RESOURCE_TYPES.STYLE:
                resource_dict['content'] = process_css(resource_dict, css_resources)
            article_resources.append(
                save_resource(article, resource_dict, rtype=rtype)
            )
    return article_resources
