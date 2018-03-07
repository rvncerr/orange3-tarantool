math.randomseed(os.time())

-- PartialSelectWidget.
function orange_partial_select(space_name, probability)
    space = box.space[space_name]
    data = space:select({})
    partial_data = {}
    for _, tuple in ipairs(data) do
        if math.random() < probability then
            table.insert(partial_data, tuple)
        end
    end
    return partial_data
end
