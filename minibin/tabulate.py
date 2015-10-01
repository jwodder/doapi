def tabulate(headers, rows):
    headers = list(headers)
    rows = list(rows)
    if not rows:
        print 'None'
    else:
        lengths = [max(len(str(x)) for x in (head,) + vals)
                   for head, vals in zip(headers, zip(*rows))]
        print '|'.join('%-*s' % szname for szname in zip(lengths, headers))
        print '|'.join('-' * sz for sz in lengths)
        for r in rows:
            print '|'.join('%-*s' % szval for szval in zip(lengths, r))
