import random

# 4
total_query = 4
# 5000
total_doc = 5000
# 6
overlap = 300
# 5
max_score = 8

k = 2
alpha = 1
num_run = 20


def main():
    upper_bound = generate_ub()
    table = create_table(upper_bound)
    ptrs_pos = [0] * total_query
    heap = []
    threshold = 0
    evaluation = 0
    curdoc = (0, 0)

    while sum(upper_bound) > threshold:
        ptr_id = []
        ptrs = []
        for i in range(total_query):
            if upper_bound[i] != 0:
                ptr_id.append(table[i][ptrs_pos[i]][0])
                ptrs.append(table[i][ptrs_pos[i]])
            else:
                ptr_id.append(99999)
                ptrs.append((99999, 99999))
        order = sorted(range(len(ptr_id)), key=lambda j: ptr_id[j])

        for _ in range(upper_bound.count(0)):
            order.pop()

        ub_list = []
        total_sum = 0
        while total_sum <= threshold:
            t = order.pop(0)
            total_sum += upper_bound[t]
            ub_list.append(t)

        pterm = ub_list.pop()
        pivot = ptrs[pterm]

        valid = True

        if pivot[0] <= curdoc[0]:
            valid = False

        for t in ub_list:
            current = ptrs[t]
            while current[0] < pivot[0]:
                valid = False
                ptrs_pos[t] += 1
                if ptrs_pos[t] >= len(table[t]):
                    upper_bound[t] = 0
                    break
                current = table[t][ptrs_pos[t]]

        if valid:
            evaluation += 1
            curdoc = pivot
            if len(heap) < k or pivot[1] >= threshold:
                total_score = 0
                for node in ptrs:
                    if node[0] == pivot[0]:
                        total_score += node[1]
                heap.append((pivot[0], total_score))
                score = []
                for node in heap:
                    score.append(node[1])
                if len(heap) > k:
                    pos = sorted(range(len(score)), key=lambda j: score[j])[0]
                    heap.pop(pos)
                    score.pop(pos)
                threshold = min(score)

            for i in range(len(ptrs)):
                if ptrs[i][0] == pivot[0]:
                    ptrs_pos[i] += 1
                    if ptrs_pos[i] >= len(table[i]):
                        upper_bound[i] = 0

    return evaluation



def generate_ub():
    upper_bound = []
    for _ in range(total_query):
        upper_bound.append(random.randint(1, max_score))
    return upper_bound


def create_table(upper_bound):
    table = []
    available_doc = list(range(1, total_doc + 1 - overlap * (total_query - 1)))

    while random.random() > 0.2:
        random.shuffle(available_doc)

    # Create posting list for the first t - 1 lists
    for i in range(total_query - 1):
        if i == 0:
            length = random.randint(overlap, len(available_doc))
        else:
            length = overlap + random.randint(0, len(available_doc))

        posting_list = []

        for _ in range(length - overlap):
            selection = random.choice(available_doc)
            available_doc.remove(selection)
            posting_list.append(selection)

        for _ in range(overlap):
            if i == 0:
                selection = random.choice(available_doc)
                available_doc.remove(selection)
                posting_list.append(selection)
            else:
                selection = random.choice(table[-1])
                while selection in posting_list:
                    selection = random.choice(table[-1])
                posting_list.append(selection)

        posting_list.sort()
        table.append(posting_list)

    # Create posting list for the last list
    for _ in range(overlap):
        selection = random.choice(table[-1])
        while selection in available_doc:
            selection = random.choice(table[-1])
        available_doc.append(selection)

    available_doc.sort()
    table.append(available_doc)

    # Done of creating table
    # Assign random score now
    for i in range(len(table)):
        for j in range(len(table[i])):
            score = random.randint(1, upper_bound[i])
            table[i][j] = (table[i][j], score)

    return table


if __name__ == '__main__':

    count = 0
    for run in range(num_run):
        random.seed(run)
        count += main()

    print(count / num_run)
