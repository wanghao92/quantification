import jqdatasdk as jq


if __name__ == '__main__':
    jq.auth('18382205937', 'Wanghao123!')
    # 查询当天剩余可调用条数
    count = jq.get_query_count()
    print(count)

    print(jq.normalize_code(['512800']))


