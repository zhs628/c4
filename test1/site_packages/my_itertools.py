
######## zip_longest zip ########
def _create_constant_iterator(value):
    def constant_generator():
        while True:
            yield value
    return constant_generator()


def zip_longest(*iterables, fillvalue=None):
    # 确保我们不是处理空列表
    if not iterables:
        return

    # 转换所有的输入到迭代器
    iterators = [iter(it) for it in iterables]

    # 追踪正在运行的迭代器的数量
    num_active = len(iterators)
    
    # 捕获StopIteration
    while num_active:
        # 使用列表收集当前轮的值
        values = []
        # 我们跟踪不再活跃的迭代器数量
        iterators_to_remove = []
        for i, it in enumerate(iterators):
            try:
                value = next(it)
                
                # for pkpy
                if value is StopIteration:
                    values.append(fillvalue)
                    # 这个迭代器结束了，我们会在这轮之后将其移除
                    iterators_to_remove.append(i)
                else:
                    values.append(value)
            except StopIteration:
                values.append(fillvalue)
                # 这个迭代器结束了，我们会在这轮之后将其移除
                iterators_to_remove.append(i)
        # 从后往前移除迭代器，防止索引混乱
        for i in reversed(iterators_to_remove):
            iterators[i] = _create_constant_iterator(fillvalue)
            num_active -= 1
        # 如果还有活跃的迭代器，就产生一个结果
        if num_active:
            yield tuple(values)

def zip(*iterables):
    # 确保我们不是处理空列表
    if not iterables:
        return

    # 转换所有的输入到迭代器
    iterators = [iter(it) for it in iterables]

    # 追踪正在运行的迭代器的数量
    num_active = len(iterators)
    
    # 捕获StopIteration
    while num_active:
        # 使用列表收集当前轮的值
        values = []

        stop_flag = False
        
        for i, it in enumerate(iterators):
            try:
                value = next(it)
                
                # for pkpy
                if value is StopIteration:
                    
                    stop_flag = True
                    break
                else:
                    values.append(value)
            except StopIteration:
                stop_flag = True
                break
        
        if stop_flag:
            break
        # 如果还有活跃的迭代器，就产生一个结果
        if num_active:
            yield tuple(values)
###################################